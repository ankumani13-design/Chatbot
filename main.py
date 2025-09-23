import streamlit as st
import pyttsx3

# ---------- VOICE FUNCTION ----------
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)  # speed of speech
    engine.setProperty("volume", 1)  # volume 0-1
    engine.say(text)
    engine.runAndWait()

# ---------- APP CONFIG ----------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 AI Assistant")

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- CHAT INPUT (Enter key to send) ----------
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    # Save user message
    st.session_state.chat_history.append(("You", user_input))

    # ---------- BOT RESPONSE (Dummy logic, replace with your model/API) ----------
    if "hi" in user_input.lower():
        bot_response = "Hello buddy! How can I help you today?"
    else:
        bot_response = f"You said: {user_input}"

    # Save bot response
    st.session_state.chat_history.append(("Bot", bot_response))

    # Speak out the bot response
    speak_text(bot_response)

    # Refresh chat
    st.rerun()

# ---------- DISPLAY CHAT HISTORY ----------
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
