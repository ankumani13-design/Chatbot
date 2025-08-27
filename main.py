import streamlit as st
import wikipedia
import re
from gtts import gTTS
import base64
import io

# --- Page Setup ---
st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="wide")

# Background & text color
st.markdown(
    """
    <style>
    body { background-color: white; color: black; }
    .chat-bubble-user {
        background-color: #DCF8C6; padding: 8px 12px; border-radius: 12px; margin: 5px;
        text-align: right; color: black;
    }
    .chat-bubble-bot {
        background-color: #F1F0F0; padding: 8px 12px; border-radius: 12px; margin: 5px;
        text-align: left; color: black;
    }
    .chat-box {
        height: 450px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 10px;
    }
    .footer-heart {
        text-align: center; margin-top: 15px; font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Chatbot")

# --- Sidebar ---
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

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Helper: TTS Generator ---
def speak_text(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode("utf-8")
    except Exception as e:
        return None

# --- Chat Input ---
user_input = st.text_input("💬 Type your message:", key="chat_input")

# --- Chat Processing ---
def process_message(user_input, feature):
    if feature == "Wikipedia":
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
    elif feature == "Medical":
        return f"📘 [Medical Placeholder] You asked: {user_input}"
    elif feature == "Science":
        return f"🔬 [Science Placeholder] You asked: {user_input}"
    elif feature == "Arts":
        return f"🎨 [Arts Placeholder] You asked: {user_input}"
    else:
        return f"I heard you say: {user_input}"

# --- Add Conversation ---
if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Process bot reply
    bot_reply = process_message(user_input, features)
    st.session_state.chat_history.append({"role": "bot", "content": bot_reply})

    # Speak reply
    audio_base64 = speak_text(bot_reply, voice_lang)
    if audio_base64:
        st.markdown(
            f"""
            <audio autoplay style="display:none">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True,
        )

# --- Show Conversation (Left-aligned like chat app) ---
st.subheader("💬 Conversation")
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-bubble-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-bot'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Sidebar Chat History ---
st.sidebar.subheader("📜 Chat History")
for msg in st.session_state.chat_history:
    role = "You" if msg["role"] == "user" else "Bot"
    st.sidebar.markdown(f"**{role}:** {msg['content']}")

# --- Footer Heart ---
st.markdown('<div class="footer-heart">❤️</div>', unsafe_allow_html=True)
