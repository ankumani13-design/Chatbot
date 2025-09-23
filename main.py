import streamlit as st
from gtts import gTTS
import base64

# ---------- VOICE FUNCTION ----------
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    file_path = "voice.mp3"
    tts.save(file_path)

    # Read the file and convert to base64
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()

    # Inject autoplay audio player
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ---------- APP CONFIG ----------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 AI Assistant")

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- CHAT INPUT ----------
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    # Save user message
    st.session_state.chat_history.append(("You", user_input))

    # ---------- BOT RESPONSE ----------
    if "hi" in user_input.lower():
        bot_response = "Hello buddy! How can I help you today?"
    else:
        bot_response = f"You said: {user_input}"

    # Save bot response
    st.session_state.chat_history.append(("Bot", bot_response))

    # Speak out the bot response (autoplay)
    speak_text(bot_response)

# ---------- DISPLAY CHAT HISTORY ----------
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
