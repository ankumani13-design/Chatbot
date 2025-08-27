import streamlit as st
import wikipedia
from gtts import gTTS
import base64
import io

# --- Page Setup ---
st.set_page_config(page_title="Smart Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Smart Chatbot")

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")
features = st.sidebar.radio(
    "Choose Feature:",
    ["General Chat", "Wikipedia", "Mathematics", "Medical", "Science", "Arts"]
)

lang_options = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese"
}
voice_lang = st.sidebar.selectbox(
    "Voice Output Language:",
    list(lang_options.keys()),
    format_func=lambda k: lang_options[k]
)

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Helper: Generate Voice ---
def speak_text(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode("utf-8")
    except Exception:
        return None

# --- Bot Logic ---
def process_message(user_text, feature):
    low = user_text.lower().strip()
    if low in ["hi", "hello", "hey"]:
        return {"summary": "Hello, how can I help you?", "url": None, "images": []}
    if low == "open google":
        return {"summary": None, "url": "https://www.google.com", "images": []}

    if feature in ["Wikipedia", "Medical", "Science", "Arts"]:
        try:
            summary = wikipedia.summary(user_text, sentences=2)
            page = wikipedia.page(user_text, auto_suggest=False)
            return {"summary": summary, "url": page.url, "images": page.images}
        except Exception:
            return {"summary": "Sorry, couldn't find anything on Wikipedia.", "url": None, "images": []}

    if feature == "Mathematics":
        try:
            result = eval(user_text)
            return {"summary": f"Answer: {result}", "url": None, "images": []}
        except Exception:
            return {"summary": "Math error! Please type a valid expression.", "url": None, "images": []}

    return {"summary": f"I heard you say: {user_text}", "url": None, "images": []}

# --- Input Field ---
user_input = st.text_input("💬 Type your message here:")

audio_base64 = None
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response = process_message(user_input, features)

    # Handle redirect to Google
    if response["url"] and response["summary"] is None:
        st.markdown(f'<meta http-equiv="refresh" content="0;url={response["url"]}">', unsafe_allow_html=True)
    else:
        bot_reply = response["summary"]
        st.session_state.chat_history.append({"role": "bot", "content": bot_reply})

        # Auto-speak
        audio_base64 = speak_text(bot_reply, voice_lang)

        # Image display
        if response["images"]:
            for img in response["images"]:
                if img.lower().endswith((".jpg", ".png")):
                    st.image(img, width=300)
                    break

        # More info link
        if response["url"]:
            st.markdown(f"[🔗 More about {user_input}]({response['url']})")

# --- Display Conversation ---
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align:right; background:#DCF8C6; padding:8px; border-radius:12px;'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:left; background:#F1F0F0; padding:8px; border-radius:12px;'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# --- Auto Voice Player ---
if audio_base64:
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:10px;">
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Footer Heart ---
st.markdown("<div style='text-align:center; font-size:22px;'>❤️</div>", unsafe_allow_html=True)
