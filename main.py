import streamlit as st
from gtts import gTTS
import base64
import os

# ---------- TEXT TO SPEECH ----------
def speak_text(text):
    tts = gTTS(text=text, lang="en")  # ✅ English-only
    file_path = "voice.mp3"
    tts.save(file_path)
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3")

# ---------- INITIALIZE SESSION STATE ----------
if "feature" not in st.session_state:
    st.session_state.feature = "Doctor Help"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {
        "Doctor Help": [],
        "Math Solver": [],
        "Assistant": []
    }

# ---------- SIDEBAR FEATURE SELECTOR ----------
st.sidebar.title("🤖 AI Assistant Features")
new_feature = st.sidebar.radio(
    "Choose a feature:",
    ("Doctor Help", "Math Solver", "Assistant"),
    key="feature_selector"
)

# Reset history when switching feature
if new_feature != st.session_state.feature:
    st.session_state.feature = new_feature

# ---------- MAIN UI ----------
st.title("🤖 AI Chatbot")

# Input box at center
user_input = st.text_input("Type your message here:", key="chat_input")

# ---------- PROCESS RESPONSE ----------
if user_input:
    feature = st.session_state.feature
    response = ""

    # Doctor Feature
    if feature == "Doctor Help":
        if user_input.lower() in ["hi", "hello"]:
            response = "Hello! I am your personal AI doctor. How can I help you today?"
        else:
            response = f"As a doctor, I suggest you: {user_input}. Please take care!"

    # Math Solver (Quantum)
    elif feature == "Math Solver":
        if user_input.lower() in ["hi", "hello"]:
            response = "Hi! I am your AI professor. How can I help you with mathematics today?"
        else:
            try:
                # Quantum-style solution simulation
                result = eval(user_input)
                response = f"Quantum solution computed: {result}"
            except:
                response = "I couldn't solve that. Please provide a valid math expression."

    # Assistant
    elif feature == "Assistant":
        if user_input.lower() in ["hi", "hello"]:
            response = "Hello! I am your AI Assistant. How can I help you today?"
        else:
            response = f"Here’s what I found for: {user_input}"

    # Store in session state
    st.session_state.chat_history[feature].append(("You", user_input))
    st.session_state.chat_history[feature].append(("Bot", response))

    # Speak out response
    speak_text(response)

# ---------- DISPLAY CHAT BELOW INPUT ----------
if st.session_state.chat_history[st.session_state.feature]:
    for sender, msg in st.session_state.chat_history[st.session_state.feature]:
        if sender == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 Bot:** {msg}")

# ---------- HEART ICON AT BOTTOM CENTER ----------
st.markdown(
    """
    <div style="position: fixed; bottom: 10px; left: 50%; 
                transform: translateX(-50%); font-size: 40px; color: red;">
        ❤️
    </div>
    """,
    unsafe_allow_html=True
)
