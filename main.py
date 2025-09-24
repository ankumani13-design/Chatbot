import streamlit as st
import sympy as sp
from gtts import gTTS
import base64
import os

# ---------------- APP CONFIG ----------------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# ---------------- VOICE FUNCTION ----------------
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    file_path = "voice.mp3"
    tts.save(file_path)

    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()

    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "feature" not in st.session_state:
    st.session_state.feature = "Assistant"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {"Assistant": [], "Doctor Help": [], "Quantum Professor": []}

# ---------------- SIDEBAR ----------------
st.sidebar.title("📜 Chat History")

feature = st.sidebar.radio("Select Feature", ("Assistant", "Doctor Help", "Quantum Professor"))

# Reset chat when switching feature
if feature != st.session_state.feature:
    st.session_state.feature = feature

# Show history for active feature in sidebar
for sender, msg in st.session_state.chat_history[feature]:
    st.sidebar.markdown(f"**{sender}:** {msg}")

# ---------------- TITLE ----------------
if feature == "Assistant":
    st.title("🤖 AI Assistant")
elif feature == "Doctor Help":
    st.title("🏥 AI Doctor")
elif feature == "Quantum Professor":
    st.title("⚛️ Quantum Professor")

# ---------------- BOT LOGIC ----------------
def get_bot_response(user_input, mode):
    user_input = user_input.lower()

    if mode == "Assistant":
        if "hi" in user_input or "hello" in user_input:
            return "Hello! I’m your AI Assistant. How can I help you?"
        return f"You said: {user_input}"

    elif mode == "Doctor Help":
        if "hi" in user_input or "hello" in user_input:
            return "Hello! I am your personal AI Doctor. How can I help you today?"
        elif "fever" in user_input:
            return "Fever is usually caused by infections (viral or bacterial). 🩺\n\n**Prevention:** Stay hydrated, rest well, and maintain hygiene.\n**Tip:** If fever persists, consult a doctor."
        elif "cold" in user_input:
            return "Cold is often caused by viral infections. 🤧\n\n**Prevention:** Wash hands, avoid cold exposure, eat vitamin C rich foods."
        elif "headache" in user_input:
            return "Headache can be due to stress, dehydration, or lack of sleep. 💆‍♀️\n\n**Prevention:** Drink water, rest properly, and manage stress."
        else:
            return "I can help with common health issues like fever, cold, and headache."

    elif mode == "Quantum Professor":
        if "hi" in user_input or "hello" in user_input:
            return "Hello! I am your AI Professor. How can I assist with your math today?"
        try:
            expr = sp.sympify(user_input)
            result = sp.simplify(expr)
            return f"✅ Solution: **{result}**"
        except Exception:
            return "Please provide a valid math expression. Example: `2+3*4` or `sin(pi/2)`."

# ---------------- MAIN CHAT ----------------
chat_container = st.container()

user_input = st.chat_input("Type your message...")

if user_input:
    # Save user input
    st.session_state.chat_history[feature].append(("You", user_input))

    # Bot response
    bot_response = get_bot_response(user_input, feature)
    st.session_state.chat_history[feature].append(("Bot", bot_response))

    # Voice output
    speak_text(bot_response)

# ---------------- DISPLAY CHAT BELOW INPUT ----------------
with chat_container:
    for sender, msg in st.session_state.chat_history[feature]:
        if sender == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 {feature}:** {msg}")
