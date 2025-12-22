import streamlit as st
import google.generativeai as genai
import random

# ============================================
# ページ設定
# ============================================
st.set_page_config(
    page_title="日本語学習アプリ 🇯🇵",
    page_icon="📚",
    layout="centered"
)

# ============================================
# カスタムCSS（スマホ対応）
# ============================================
st.markdown("""
<style>
    /* 全体のフォントサイズ調整 */
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* 大きな文字表示用 */
    .big-text {
        font-size: 2.5rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* クイズオプションボタン */
    .stButton > button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
        margin: 0.25rem 0;
    }
    
    /* 正解/不正解の表示 */
    .correct {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3rem;
    }
    
    .incorrect {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3rem;
    }
    
    /* フラッシュカード */
    .flashcard {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* チャットメッセージ */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    
    .ai-message {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# APIキー管理（ハイブリッド方式）
# ============================================
def get_api_key():
    """st.secretsを優先、なければサイドバーから入力"""
    # 1. まずst.secretsを確認
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        if api_key:
            return api_key
    except (KeyError, FileNotFoundError):
        pass
    
    # 2. Secretsにない場合、サイドバーから入力
    with st.sidebar:
        st.warning("⚠️ APIキーが設定されていません")
        api_key = st.text_input(
            "Gemini APIキーを入力",
            type="password",
            help="Google AI StudioでAPIキーを取得できます"
        )
        if api_key:
            st.success("✅ APIキー入力済み")
            return api_key
    
    return None

# ============================================
# Gemini API初期化
# ============================================
def init_gemini(api_key):
    """Gemini APIを初期化"""
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"API初期化エラー: {e}")
        return None

# ============================================
# セッション状態の初期化
# ============================================
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False
if "score" not in st.session_state:
    st.session_state.score = {"correct": 0, "total": 0}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "flashcard_index" not in st.session_state:
    st.session_state.flashcard_index = 0
if "flashcard_show_answer" not in st.session_state:
    st.session_state.flashcard_show_answer = False

# ============================================
# メイン
# ============================================
st.title("📚 日本語学習アプリ")
st.caption("中国の小学生のための日本語練習 🇨🇳➡️🇯🇵")

# APIキー取得
api_key = get_api_key()

# サイドバー：モード選択
with st.sidebar:
    st.header("🎮 モードを選ぼう")
    mode = st.radio(
        "学習モード",
        ["🎯 熟語クイズ", "🤖 先生AIチャット", "🔍 間違い探し", "📖 フラッシュカード"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # スコア表示
    if st.session_state.score["total"] > 0:
        correct = st.session_state.score["correct"]
        total = st.session_state.score["total"]
        st.metric("今日のスコア", f"{correct}/{total}", f"{int(correct/total*100)}%")

# ============================================
# 熟語クイズモード
# ============================================
if mode == "🎯 熟語クイズ":
    st.header("🎯 熟語クイズ")
    st.write("正しい読み方を選んでね！")
    
    if not api_key:
        st.info("👈 左のサイドバーからAPIキーを入力してください")
    else:
        model = init_gemini(api_key)
        
        if model:
            # 新しい問題を生成
            if st.button("🆕 新しい問題", use_container_width=True) or st.session_state.quiz_data is None:
                with st.spinner("問題を作っています..."):
                    try:
                        prompt = """
あなたは日本語教師です。中国人小学生向けに熟語クイズを1問作ってください。

以下の形式でJSONで出力してください（他の文字は一切不要）：
{
    "word": "漢字の熟語（2-3文字）",
    "correct_reading": "正しい読み方（ひらがな）",
    "wrong_readings": ["間違い1", "間違い2", "間違い3"],
    "meaning_chinese": "中国語での意味",
    "example_sentence": "例文（ふりがな付き）"
}

難易度は小学5年生レベルで。
"""
                        response = model.generate_content(prompt)
                        # JSONを抽出
                        import json
                        text = response.text.strip()
                        # ```json と ``` を除去
                        if "```json" in text:
                            text = text.split("```json")[1].split("```")[0]
                        elif "```" in text:
                            text = text.split("```")[1].split("```")[0]
                        
                        quiz_data = json.loads(text.strip())
                        st.session_state.quiz_data = quiz_data
                        st.session_state.quiz_answered = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"問題生成エラー: {e}")
            
            # クイズを表示
            if st.session_state.quiz_data:
                quiz = st.session_state.quiz_data
                
                # 熟語を大きく表示
                st.markdown(f'<div class="big-text">{quiz["word"]}</div>', unsafe_allow_html=True)
                st.caption(f"🇨🇳 中国語: {quiz.get('meaning_chinese', '')}")
                
                if not st.session_state.quiz_answered:
                    # 選択肢を作成（シャッフル）
                    options = [quiz["correct_reading"]] + quiz["wrong_readings"]
                    random.shuffle(options)
                    
                    st.write("**この熟語の読み方は？**")
                    
                    cols = st.columns(2)
                    for i, option in enumerate(options):
                        with cols[i % 2]:
                            if st.button(option, key=f"opt_{i}", use_container_width=True):
                                st.session_state.quiz_answered = True
                                st.session_state.score["total"] += 1
                                
                                if option == quiz["correct_reading"]:
                                    st.session_state.score["correct"] += 1
                                    st.session_state.last_result = "correct"
                                else:
                                    st.session_state.last_result = "incorrect"
                                st.rerun()
                else:
                    # 結果表示
                    if st.session_state.get("last_result") == "correct":
                        st.markdown('<div class="correct">🎉 正解！すごい！</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="incorrect">😢 残念... 正解は「{quiz["correct_reading"]}」</div>', unsafe_allow_html=True)
                    
                    st.info(f"📝 例文: {quiz.get('example_sentence', '')}")

# ============================================
# 先生AIチャットモード
# ============================================
elif mode == "🤖 先生AIチャット":
    st.header("🤖 先生AIに質問しよう")
    st.write("日本語について何でも聞いてね！")
    
    if not api_key:
        st.info("👈 左のサイドバーからAPIキーを入力してください")
    else:
        model = init_gemini(api_key)
        
        if model:
            # チャット履歴表示
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message ai-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
            
            # 入力フォーム
            user_input = st.chat_input("質問を入力してね...")
            
            if user_input:
                # ユーザーメッセージを追加
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # AIの応答を生成
                with st.spinner("考え中..."):
                    try:
                        system_prompt = """
あなたは優しい日本語の先生です。中国人の小学5年生に日本語を教えています。
以下のルールを守ってください：
1. 簡単な日本語で説明する
2. 必要に応じて中国語での説明も加える
3. 例文を使って分かりやすく教える
4. 励ましの言葉を入れる
5. 長すぎる回答は避ける（3-5文程度）
"""
                        full_prompt = f"{system_prompt}\n\n生徒の質問: {user_input}"
                        response = model.generate_content(full_prompt)
                        ai_response = response.text
                        
                        st.session_state.chat_history.append({"role": "ai", "content": ai_response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"エラー: {e}")
            
            # クリアボタン
            if st.button("🗑️ チャットをクリア"):
                st.session_state.chat_history = []
                st.rerun()

# ============================================
# 間違い探しモード
# ============================================
elif mode == "🔍 間違い探し":
    st.header("🔍 間違い探し")
    st.write("文の中の間違いを見つけてね！")
    
    if not api_key:
        st.info("👈 左のサイドバーからAPIキーを入力してください")
    else:
        model = init_gemini(api_key)
        
        if model:
            if "mistake_data" not in st.session_state:
                st.session_state.mistake_data = None
            if "mistake_answered" not in st.session_state:
                st.session_state.mistake_answered = False
            
            if st.button("🆕 新しい問題", use_container_width=True) or st.session_state.mistake_data is None:
                with st.spinner("問題を作っています..."):
                    try:
                        prompt = """
中国人小学生向けの「間違い探し」問題を1つ作ってください。
日本語の文章の中に1つだけ間違いがあります。

以下の形式でJSONで出力（他の文字は不要）：
{
    "sentence": "間違いを含む文（15-25文字）",
    "mistake": "間違っている部分",
    "correct": "正しい表現",
    "explanation": "なぜ間違いなのか（中国語で簡単に説明）"
}

間違いの種類：助詞の間違い、送り仮名の間違い、漢字の読み間違いなど
"""
                        response = model.generate_content(prompt)
                        import json
                        text = response.text.strip()
                        if "```json" in text:
                            text = text.split("```json")[1].split("```")[0]
                        elif "```" in text:
                            text = text.split("```")[1].split("```")[0]
                        
                        st.session_state.mistake_data = json.loads(text.strip())
                        st.session_state.mistake_answered = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"問題生成エラー: {e}")
            
            if st.session_state.mistake_data:
                data = st.session_state.mistake_data
                
                st.markdown(f'<div class="big-text" style="font-size: 1.5rem;">{data["sentence"]}</div>', unsafe_allow_html=True)
                
                if not st.session_state.mistake_answered:
                    user_answer = st.text_input("間違いはどこ？（間違っている部分を入力）")
                    
                    if st.button("答え合わせ", use_container_width=True):
                        st.session_state.mistake_answered = True
                        st.session_state.score["total"] += 1
                        
                        if user_answer.strip() == data["mistake"]:
                            st.session_state.score["correct"] += 1
                            st.session_state.mistake_result = "correct"
                        else:
                            st.session_state.mistake_result = "incorrect"
                        st.rerun()
                else:
                    if st.session_state.get("mistake_result") == "correct":
                        st.markdown('<div class="correct">🎉 正解！よく見つけたね！</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="incorrect">😢 残念... 間違いは「{data["mistake"]}」</div>', unsafe_allow_html=True)
                    
                    st.success(f"✅ 正しくは: {data['correct']}")
                    st.info(f"📖 説明: {data['explanation']}")

# ============================================
# フラッシュカードモード
# ============================================
elif mode == "📖 フラッシュカード":
    st.header("📖 フラッシュカード")
    st.write("単語を覚えよう！")
    
    # 事前に用意した単語リスト（API不要）
    flashcards = [
        {"word": "学校", "reading": "がっこう", "meaning": "学校 xuéxiào", "example": "学校に行きます。"},
        {"word": "友達", "reading": "ともだち", "meaning": "朋友 péngyou", "example": "友達と遊びます。"},
        {"word": "先生", "reading": "せんせい", "meaning": "老师 lǎoshī", "example": "先生に質問します。"},
        {"word": "勉強", "reading": "べんきょう", "meaning": "学习 xuéxí", "example": "日本語を勉強します。"},
        {"word": "家族", "reading": "かぞく", "meaning": "家人 jiārén", "example": "家族は5人です。"},
        {"word": "天気", "reading": "てんき", "meaning": "天气 tiānqì", "example": "今日の天気はいいです。"},
        {"word": "食事", "reading": "しょくじ", "meaning": "饭/用餐 fàn", "example": "食事の時間です。"},
        {"word": "音楽", "reading": "おんがく", "meaning": "音乐 yīnyuè", "example": "音楽を聴きます。"},
        {"word": "運動", "reading": "うんどう", "meaning": "运动 yùndòng", "example": "運動が好きです。"},
        {"word": "宿題", "reading": "しゅくだい", "meaning": "作业 zuòyè", "example": "宿題を忘れました。"},
    ]
    
    idx = st.session_state.flashcard_index % len(flashcards)
    card = flashcards[idx]
    
    # カード表示
    if not st.session_state.flashcard_show_answer:
        st.markdown(f'<div class="flashcard">{card["word"]}</div>', unsafe_allow_html=True)
        st.caption("👆 この漢字、読めるかな？")
    else:
        st.markdown(f'<div class="flashcard">{card["reading"]}</div>', unsafe_allow_html=True)
        st.success(f"🇨🇳 意味: {card['meaning']}")
        st.info(f"📝 例文: {card['example']}")
    
    # ボタン
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 めくる", use_container_width=True):
            st.session_state.flashcard_show_answer = not st.session_state.flashcard_show_answer
            st.rerun()
    with col2:
        if st.button("➡️ 次へ", use_container_width=True):
            st.session_state.flashcard_index += 1
            st.session_state.flashcard_show_answer = False
            st.rerun()
    
    # 進捗
    st.progress((idx + 1) / len(flashcards))
    st.caption(f"カード {idx + 1} / {len(flashcards)}")

# ============================================
# フッター
# ============================================
st.divider()
st.caption("Made with ❤️ for Chinese students learning Japanese")
