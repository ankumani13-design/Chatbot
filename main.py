import streamlit as st
from gtts import gTTS
import base64
import os
import sympy as sp

# ---------- VOICE FUNCTION ----------
def speak_text(text):
    try:
        tts = gTTS(text=text, lang="en")
        file_path = "voice.mp3"
        tts.save(file_path)
        audio_file = open(file_path, "rb")
        audio_bytes = audio_file.read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Voice error: {e}")

# ---------- INITIALIZE SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "role" not in st.session_state:
    st.session_state.role = "Assistant"

# ---------- SIDEBAR ----------
role = st.sidebar.selectbox("Choose Role", ["Assistant", "AI Doctor", "Professor Quantum"])

# Reset chat when switching role
if role != st.session_state.role:
    st.session_state.chat_history = []
    st.session_state.role = role

# ---------- TITLE ----------
st.title(f"🤖 {role}")

# ---------- HELPER FUNCTIONS ----------
def doctor_reply(user_input):
    if "fever" in user_input.lower():
        return "Fever may be caused by infections or flu. Prevention includes hydration, rest, and consulting a doctor if persistent."
    elif "cold" in user_input.lower():
        return "Cold is usually caused by viral infections. Prevention includes handwashing, avoiding crowded places, and boosting immunity."
    else:
        return f"I’m your AI Doctor. You said: {user_input}"

def quantum_reply(user_input):
    try:
        expr = sp.sympify(user_input)
        result = sp.simplify(expr)
        return f"The simplified result of {user_input} is: {result}"
    except:
        if "2+2" in user_input:
            return "2 + 2 = 4"
        elif "step by step" in user_input.lower():
            return "Please enter an expression and I’ll solve it step by step."
        return f"I’m Professor Quantum. You said: {user_input}"

def quantum_step_by_step(expression):
    try:
        steps = []
        expr = sp.sympify(expression)

        # Expand and simplify separately
        expanded = sp.expand(expr)
        simplified = sp.simplify(expr)

        steps.append(f"Original Expression: {expr}")
        if expanded != expr:
            steps.append(f"Step 1: Expand → {expanded}")
        steps.append(f"Step 2: Simplify → {simplified}")

        return "\n".join(steps)
    except Exception as e:
        return f"Sorry, I couldn’t process that expression. Error: {e}"

# ---------- INPUT ----------
user_input = st.text_input("Type your message...", key="main_input")

if user_input:
    # Add user message
    st.session_state.chat_history.append(("user", user_input))

    # Bot reply logic
    if role == "Assistant":
        bot_reply = f"You said: {user_input}"
    elif role == "AI Doctor":
        bot_reply = doctor_reply(user_input)
    elif role == "Professor Quantum":
        if "step by step" in user_input.lower():
            # get last expression from history if available
            last_expr = None
            for sender, msg in reversed(st.session_state.chat_history):
                if sender == "user" and msg != user_input:
                    last_expr = msg
                    break
            if last_expr:
                bot_reply = quantum_step_by_step(last_expr)
            else:
                bot_reply = "Please provide an expression before asking for step by step."
        else:
            bot_reply = quantum_reply(user_input)
    else:
        bot_reply = "I’m here to help!"

    # Add bot reply
    st.session_state.chat_history.append(("bot", bot_reply))

    # Speak automatically
    speak_text(bot_reply)

# ---------- DISPLAY CHAT BELOW INPUT ----------
st.markdown("### Chat History")
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **{role}:** {msg}")
