import streamlit as st
import random
import os
from groq import Groq

# ============================================
# Groq API設定
# ============================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

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
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .big-text {
        font-size: 2.5rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
        margin: 0.25rem 0;
    }
    
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
</style>
""", unsafe_allow_html=True)

# ============================================
# 熟語クイズデータ（20問）
# ============================================
QUIZ_DATA = [
    {"word": "勉強", "correct_reading": "べんきょう", "wrong_readings": ["べんきよう", "べんきゅう", "べんこう"], "meaning_chinese": "学习 xuéxí", "example": "毎日日本語を勉強します。"},
    {"word": "学校", "correct_reading": "がっこう", "wrong_readings": ["がくこう", "がこう", "がっこ"], "meaning_chinese": "学校 xuéxiào", "example": "学校は楽しいです。"},
    {"word": "友達", "correct_reading": "ともだち", "wrong_readings": ["ゆうたち", "ともたち", "ゆうだち"], "meaning_chinese": "朋友 péngyou", "example": "友達と遊びます。"},
    {"word": "先生", "correct_reading": "せんせい", "wrong_readings": ["せんしょう", "さきせい", "せいせん"], "meaning_chinese": "老师 lǎoshī", "example": "先生に質問します。"},
    {"word": "家族", "correct_reading": "かぞく", "wrong_readings": ["いえぞく", "かそく", "けぞく"], "meaning_chinese": "家人 jiārén", "example": "家族は5人です。"},
    {"word": "天気", "correct_reading": "てんき", "wrong_readings": ["てんけ", "あめき", "てんぎ"], "meaning_chinese": "天气 tiānqì", "example": "今日の天気はいいです。"},
    {"word": "食事", "correct_reading": "しょくじ", "wrong_readings": ["たべじ", "しょくし", "しょくに"], "meaning_chinese": "饭/用餐 fàn", "example": "食事の時間です。"},
    {"word": "音楽", "correct_reading": "おんがく", "wrong_readings": ["おとがく", "いんがく", "おんらく"], "meaning_chinese": "音乐 yīnyuè", "example": "音楽を聴きます。"},
    {"word": "運動", "correct_reading": "うんどう", "wrong_readings": ["うんとう", "はこどう", "うどう"], "meaning_chinese": "运动 yùndòng", "example": "運動が好きです。"},
    {"word": "宿題", "correct_reading": "しゅくだい", "wrong_readings": ["やどだい", "しゅくたい", "しゅだい"], "meaning_chinese": "作业 zuòyè", "example": "宿題を忘れました。"},
    {"word": "図書館", "correct_reading": "としょかん", "wrong_readings": ["ずしょかん", "としょがん", "とうしょかん"], "meaning_chinese": "图书馆 túshūguǎn", "example": "図書館で本を読みます。"},
    {"word": "病院", "correct_reading": "びょういん", "wrong_readings": ["やまいん", "びょいん", "びょうえん"], "meaning_chinese": "医院 yīyuàn", "example": "病院に行きます。"},
    {"word": "電車", "correct_reading": "でんしゃ", "wrong_readings": ["でんくるま", "でんしや", "てんしゃ"], "meaning_chinese": "电车 diànchē", "example": "電車で学校に行きます。"},
    {"word": "買物", "correct_reading": "かいもの", "wrong_readings": ["ばいもの", "かいぶつ", "かいもつ"], "meaning_chinese": "购物 gòuwù", "example": "買物に行きましょう。"},
    {"word": "料理", "correct_reading": "りょうり", "wrong_readings": ["りょうに", "りょり", "りようり"], "meaning_chinese": "料理 liàolǐ", "example": "母は料理が上手です。"},
    {"word": "映画", "correct_reading": "えいが", "wrong_readings": ["えが", "えいか", "ようが"], "meaning_chinese": "电影 diànyǐng", "example": "映画を見ます。"},
    {"word": "写真", "correct_reading": "しゃしん", "wrong_readings": ["しゃじん", "かきしん", "しゃちん"], "meaning_chinese": "照片 zhàopiàn", "example": "写真を撮ります。"},
    {"word": "新聞", "correct_reading": "しんぶん", "wrong_readings": ["しんもん", "あらぶん", "しんぷん"], "meaning_chinese": "报纸 bàozhǐ", "example": "新聞を読みます。"},
    {"word": "野菜", "correct_reading": "やさい", "wrong_readings": ["のさい", "やさき", "のなさい"], "meaning_chinese": "蔬菜 shūcài", "example": "野菜を食べます。"},
    {"word": "果物", "correct_reading": "くだもの", "wrong_readings": ["かぶつ", "はたもの", "くだぶつ"], "meaning_chinese": "水果 shuǐguǒ", "example": "果物が好きです。"},
]

# ============================================
# 間違い探しデータ（8問）
# ============================================
MISTAKE_DATA = [
    {"sentence": "わたしは学校が行きます。", "mistake": "が", "correct": "に", "explanation": "「行く」是移动动词，应该用「に」表示目的地。"},
    {"sentence": "りんごは赤くいです。", "mistake": "くい", "correct": "い", "explanation": "形容词「赤い」不需要加「く」。正确是「赤いです」。"},
    {"sentence": "本を読むのが好きいです。", "mistake": "好きい", "correct": "好き", "explanation": "「好き」是な形容词，不需要加「い」。"},
    {"sentence": "昨日、友達を会いました。", "mistake": "を", "correct": "に", "explanation": "「会う」用「に」表示见面的对象，不用「を」。"},
    {"sentence": "この本は面白です。", "mistake": "面白", "correct": "面白い", "explanation": "「面白い」是い形容词，需要「い」结尾。"},
    {"sentence": "日本語を話すことがでます。", "mistake": "でます", "correct": "できます", "explanation": "「できる」的ます形是「できます」，不是「でます」。"},
    {"sentence": "彼女は歌を上手です。", "mistake": "を", "correct": "が", "explanation": "「上手」前面用「が」，不用「を」。"},
    {"sentence": "今日は暑いなので、アイスを食べます。", "mistake": "暑いな", "correct": "暑い", "explanation": "い形容词后面直接加「ので」，不需要「な」。"},
]

# ============================================
# フラッシュカードデータ（10枚）
# ============================================
FLASHCARDS = [
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

# ============================================
# セッション状態の初期化
# ============================================
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = random.randint(0, len(QUIZ_DATA) - 1)
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False
if "score" not in st.session_state:
    st.session_state.score = {"correct": 0, "total": 0}
if "flashcard_index" not in st.session_state:
    st.session_state.flashcard_index = 0
if "flashcard_show_answer" not in st.session_state:
    st.session_state.flashcard_show_answer = False
if "mistake_index" not in st.session_state:
    st.session_state.mistake_index = random.randint(0, len(MISTAKE_DATA) - 1)
if "mistake_answered" not in st.session_state:
    st.session_state.mistake_answered = False

# ============================================
# メイン
# ============================================
st.title("📚 日本語学習アプリ")
st.caption("中国の小学生のための日本語練習 🇨🇳➡️🇯🇵")

# サイドバー
with st.sidebar:
    st.header("🎮 モードを選ぼう")
    mode = st.radio(
        "学習モード",
        ["🎯 熟語クイズ", "🔍 間違い探し", "📖 フラッシュカード", "🤖 AIチューター", "✨ AI問題生成"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if st.session_state.score["total"] > 0:
        correct = st.session_state.score["correct"]
        total = st.session_state.score["total"]
        st.metric("今日のスコア", f"{correct}/{total}", f"{int(correct/total*100)}%")
    
    st.divider()
    st.caption("🚀 オフライン対応！いつでも使える")

# ============================================
# 熟語クイズモード
# ============================================
if mode == "🎯 熟語クイズ":
    st.header("🎯 熟語クイズ")
    st.write("正しい読み方を選んでね！")
    
    if st.button("🆕 新しい問題", use_container_width=True):
        st.session_state.quiz_index = random.randint(0, len(QUIZ_DATA) - 1)
        st.session_state.quiz_answered = False
        st.rerun()
    
    quiz = QUIZ_DATA[st.session_state.quiz_index]
    
    st.markdown(f'<div class="big-text">{quiz["word"]}</div>', unsafe_allow_html=True)
    st.caption(f"🇨🇳 中国語: {quiz['meaning_chinese']}")
    
    if not st.session_state.quiz_answered:
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
        if st.session_state.get("last_result") == "correct":
            st.markdown('<div class="correct">🎉 正解！すごい！</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="incorrect">😢 残念... 正解は「{quiz["correct_reading"]}」</div>', unsafe_allow_html=True)
        
        st.info(f"📝 例文: {quiz['example']}")

# ============================================
# 間違い探しモード
# ============================================
elif mode == "🔍 間違い探し":
    st.header("🔍 間違い探し")
    st.write("文の中の間違いを見つけてね！")
    
    if st.button("🆕 新しい問題", use_container_width=True):
        st.session_state.mistake_index = random.randint(0, len(MISTAKE_DATA) - 1)
        st.session_state.mistake_answered = False
        st.rerun()
    
    data = MISTAKE_DATA[st.session_state.mistake_index]
    
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
    
    idx = st.session_state.flashcard_index % len(FLASHCARDS)
    card = FLASHCARDS[idx]
    
    if not st.session_state.flashcard_show_answer:
        st.markdown(f'<div class="flashcard">{card["word"]}</div>', unsafe_allow_html=True)
        st.caption("👆 この漢字、読めるかな？")
    else:
        st.markdown(f'<div class="flashcard">{card["reading"]}</div>', unsafe_allow_html=True)
        st.success(f"🇨🇳 意味: {card['meaning']}")
        st.info(f"📝 例文: {card['example']}")
    
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
    
    st.progress((idx + 1) / len(FLASHCARDS))
    st.caption(f"カード {idx + 1} / {len(FLASHCARDS)}")

# ============================================
# AIチューターモード
# ============================================
elif mode == "🤖 AIチューター":
    st.header("🤖 AIチューター")
    st.write("漢字や熟語の意味を教えてもらおう！")
    
    user_input = st.text_input("🔤 調べたい漢字・熟語を入力", placeholder="例: 勉強、学校、友達...")
    
    if st.button("📚 意味を調べる", use_container_width=True) and user_input:
        with st.spinner("AIが調べています..."):
            try:
                prompt = f"""あなたは中国の小学生に日本語を教える優しい先生です。
以下の日本語の漢字・熟語について教えてください：

「{user_input}」

以下の形式で回答してください：
📖 読み方: （ひらがなで）
🇨🇳 中国語の意味: （簡体字で、ピンイン付き）
📝 例文: （簡単な日本語の例文を1つ）
💡 覚え方のコツ: （中国語との関連や覚えやすいヒント）

回答は小学生にもわかりやすく、短くまとめてください。"""
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1024
                )
                st.markdown("---")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
    
    st.divider()
    st.caption("💡 ヒント: 漢字1文字でも、熟語でも調べられます！")

# ============================================
# AI問題生成モード
# ============================================
elif mode == "✨ AI問題生成":
    st.header("✨ AI問題生成")
    st.write("AIが新しい問題を作ってくれるよ！")
    
    difficulty = st.select_slider(
        "難易度を選ぼう",
        options=["かんたん", "ふつう", "むずかしい"],
        value="ふつう"
    )
    
    if "ai_quiz" not in st.session_state:
        st.session_state.ai_quiz = None
    if "ai_quiz_answered" not in st.session_state:
        st.session_state.ai_quiz_answered = False
    
    if st.button("🎲 新しい問題を作る", use_container_width=True):
        with st.spinner("AIが問題を考えています..."):
            try:
                level_desc = {
                    "かんたん": "小学1-2年生レベルの簡単な漢字（日、月、火、水、山、川など）",
                    "ふつう": "小学3-4年生レベルの漢字（勉強、学校、友達など）",
                    "むずかしい": "小学5-6年生レベルの漢字（経済、政治、環境など）"
                }
                
                prompt = f"""あなたは日本語クイズの出題者です。
{level_desc[difficulty]}から1つの熟語を選び、読み方クイズを作ってください。

以下のJSON形式で回答してください（余計な説明は不要）:
{{
  "word": "熟語",
  "correct_reading": "正しい読み方（ひらがな）",
  "wrong_readings": ["間違い1", "間違い2", "間違い3"],
  "meaning_chinese": "中国語の意味（ピンイン付き）",
  "example": "例文"
}}"""
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1024
                )
                response_text = response.choices[0].message.content.strip()
                
                # JSONを抽出（```json ... ``` の形式にも対応）
                import json
                import re
                
                # マークダウンのコードブロックを除去
                if "```json" in response_text:
                    response_text = re.sub(r'```json\s*', '', response_text)
                    response_text = re.sub(r'```\s*', '', response_text)
                elif "```" in response_text:
                    response_text = re.sub(r'```\s*', '', response_text)
                
                # JSONを抽出（ネストされたオブジェクトや配列に対応）
                try:
                    # 最初の { から最後の } までを抽出
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx + 1]
                        quiz_data = json.loads(json_str)
                        st.session_state.ai_quiz = quiz_data
                        st.session_state.ai_quiz_answered = False
                    else:
                        st.error("問題の生成に失敗しました。もう一度お試しください。")
                except json.JSONDecodeError as je:
                    st.error(f"JSONの解析に失敗しました: {str(je)}")
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
        st.rerun()
    
    # 生成された問題を表示
    if st.session_state.ai_quiz:
        quiz = st.session_state.ai_quiz
        
        st.markdown(f'<div class="big-text">{quiz["word"]}</div>', unsafe_allow_html=True)
        st.caption(f"🇨🇳 中国語: {quiz['meaning_chinese']}")
        
        if not st.session_state.ai_quiz_answered:
            options = [quiz["correct_reading"]] + quiz["wrong_readings"]
            random.shuffle(options)
            
            st.write("**この熟語の読み方は？**")
            
            cols = st.columns(2)
            for i, option in enumerate(options):
                with cols[i % 2]:
                    if st.button(option, key=f"ai_opt_{i}", use_container_width=True):
                        st.session_state.ai_quiz_answered = True
                        st.session_state.score["total"] += 1
                        
                        if option == quiz["correct_reading"]:
                            st.session_state.score["correct"] += 1
                            st.session_state.ai_result = "correct"
                        else:
                            st.session_state.ai_result = "incorrect"
                        st.rerun()
        else:
            if st.session_state.get("ai_result") == "correct":
                st.markdown('<div class="correct">🎉 正解！すごい！</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="incorrect">😢 残念... 正解は「{quiz["correct_reading"]}」</div>', unsafe_allow_html=True)
            
            st.info(f"📝 例文: {quiz['example']}")

# ============================================
# フッター
# ============================================
st.divider()
st.caption("Made with ❤️ for Chinese students learning Japanese | Powered by Gemini AI 🤖")

