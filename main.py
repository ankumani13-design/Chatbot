import streamlit as st
import sympy as sp
from gtts import gTTS
import base64
import os

# ---------------- APP CONFIG ----------------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# ---------------- VOICE FUNCTION ----------------
def speak_text(text):
    try:
        tts = gTTS(text=text, lang="en", slow=False)
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
    except:
        st.warning("⚠️ Voice output failed. Please check gTTS.")

# ---------------- SESSION STATE ----------------
if "feature" not in st.session_state:
    st.session_state.feature = "Assistant"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {"Assistant": [], "Doctor Help": [], "Quantum Professor": []}
if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0  # used to reset text box

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
            return "🤒 Fever is usually caused by infections.\n\n**Prevention:** Stay hydrated, rest, and maintain hygiene."
        elif "cold" in user_input:
            return "🤧 Cold is often caused by viral infections.\n\n**Prevention:** Wash hands, stay warm, eat vitamin C."
        elif "headache" in user_input:
            return "🤕 Headache can be due to stress or dehydration.\n\n**Prevention:** Drink water, sleep well, reduce screen time."
        else:
            return "I can help with common health issues like fever, cold, and headache."

    elif mode == "Quantum Professor":
        if "hi" in user_input or "hello" in user_input:
            return "Hello! I am your AI Professor. How can I assist with your math today?"
        try:
            expr = sp.sympify(user_input)
            simplified = sp.simplify(expr)
            return f"✅ Simplified Result: **{simplified}**"
        except Exception:
            return "Please provide a valid math expression. Example: `2+3*4` or `sin(pi/2)`."

# ---------------- MAIN CHAT ----------------
chat_container = st.container()

# Input box with dynamic key (resets automatically after each message)
user_input = st.text_input("Type your message...", key=f"input_{st.session_state.input_counter}")

if user_input:
    # Save user input
    st.session_state.chat_history[feature].append(("You", user_input))

    # Bot response
    bot_response = get_bot_response(user_input, feature)
    st.session_state.chat_history[feature].append(("Bot", bot_response))

    # Voice output
    speak_text(bot_response)

    # Force input box reset by increasing counter
    st.session_state.input_counter += 1
    st.rerun()

# ---------------- DISPLAY CHAT BELOW INPUT ----------------
with chat_container:
    for sender, msg in st.session_state.chat_history[feature]:
        if sender == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 {feature}:** {msg}")
