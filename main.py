import streamlit as st
import wikipedia
from gtts import gTTS
import base64
import io

# --- Page Setup ---
st.set_page_config(page_title="Jarvis Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Jarvis Chatbot")

# Sidebar
st.sidebar.header("⚙️ Settings")
features = st.sidebar.radio("Choose Feature:", ["General Chat", "Wikipedia", "Mathematics", "Medical", "Science", "Arts"])

lang_options = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese"
}
voice_lang = st.sidebar.selectbox("Voice Output Language:", list(lang_options.keys()), format_func=lambda k: lang_options[k])

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Voice Output ---
def speak_text(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode("utf-8")
    except Exception:
        return None

# --- Message Processing ---
def process_message(user_input, feature):
    if user_input.lower().strip() in ["hi", "hello", "hey"]:
        return "Hello, my name is Jarvis. How can I help you?"

    if feature in ["Wikipedia", "Medical", "Science", "Arts"]:
        try:
            summary = wikipedia.summary(user_input, sentences=2)
            page = wikipedia.page(user_input, auto_suggest=False)
            return {"summary": summary, "url": page.url, "images": page.images}
        except:
            return {"summary": "Sorry, I couldn't find anything on Wikipedia.", "url": None, "images": []}
    elif feature == "Mathematics":
        try:
            result = eval(user_input)
            return {"summary": f"Answer: {result}", "url": None, "images": []}
        except:
            return {"summary": "Math error! Please type a valid expression (e.g., 5*10+2).", "url": None, "images": []}
    else:
        return {"summary": f"I heard you say: {user_input}", "url": None, "images": []}

# --- Input Section ---
user_input = st.text_input("💬 Type your message here:")

# --- Process Input ---
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = process_message(user_input, features)

    # Handle Wikipedia type
    if isinstance(response, dict):
        bot_reply = response["summary"]
        st.session_state.chat_history.append({"role": "bot", "content": bot_reply})

        # Voice reply
        audio_base64 = speak_text(bot_reply, voice_lang)
        if audio_base64:
            st.markdown(
                f"""
                <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                """,
                unsafe_allow_html=True,
            )

        # Show image (first valid image if available)
        if response["images"]:
            for img in response["images"]:
                if img.lower().endswith((".jpg", ".png")):
                    st.image(img, width=300)
                    break

        # Show link
        if response["url"]:
            st.markdown(f"[🔗 More about {user_input}]({response['url']})")

    else:
        bot_reply = response
        st.session_state.chat_history.append({"role": "bot", "content": bot_reply})

# --- Show Chat History ---
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align:right; background:#DCF8C6; padding:8px; border-radius:12px;'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:left; background:#F1F0F0; padding:8px; border-radius:12px;'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# Footer Heart
st.markdown("<div style='text-align:center; font-size:22px;'>❤️</div>", unsafe_allow_html=True)
