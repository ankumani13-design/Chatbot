import streamlit as st
import wikipedia
from gtts import gTTS
import base64
import io
import speech_recognition as sr

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
            return summary
        except:
            return "Sorry, I couldn't find anything on Wikipedia."
    elif feature == "Mathematics":
        try:
            result = eval(user_input)
            return f"Answer: {result}"
        except:
            return "Math error! Please type a valid expression (e.g., 5*10+2)."
    else:
        return f"I heard you say: {user_input}"

# --- Input Section (Text + Mic Icon) ---
col1, col2 = st.columns([8,1])

with col1:
    user_input = st.text_input("💬 Type your message here:", key="text_input")

with col2:
    if st.button("🎤"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            st.info("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            user_input = recognizer.recognize_google(audio)
            st.success(f"🧑 You said: {user_input}")
        except:
            st.error("Sorry, I couldn't recognize your voice.")
            user_input = None

# --- Process Input ---
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    bot_reply = process_message(user_input, features)
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

# --- Show Chat History ---
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align:right; background:#DCF8C6; padding:8px; border-radius:12px;'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:left; background:#F1F0F0; padding:8px; border-radius:12px;'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# Footer Heart
st.markdown("<div style='text-align:center; font-size:22px;'>❤️</div>", unsafe_allow_html=True)
