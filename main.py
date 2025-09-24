import streamlit as st
from gtts import gTTS
import base64
import wikipedia
from sympy import symbols, Eq, solve, simplify
from sympy.parsing.sympy_parser import parse_expr

# ---------- VOICE FUNCTION ----------
def speak_text(text):
    """Convert text to speech and autoplay"""
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
    except Exception:
        pass

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
    user_input_lower = user_input.lower()
    if "hi" in user_input_lower or "hello" in user_input_lower:
        return "Hello! I am your personal AI Doctor. How can I help you?"
    elif "fever" in user_input_lower:
        return (
            "🤒 Fever\n"
            "• Cause: Usually infections like flu or cold.\n"
            "• Prevention: Hydration, rest, maintain hygiene.\n"
            "• Remedy: Take paracetamol and consult a doctor if high fever persists."
        )
    elif "cold" in user_input_lower:
        return (
            "🤧 Cold\n"
            "• Cause: Viral infection of upper respiratory tract.\n"
            "• Prevention: Wash hands, stay warm.\n"
            "• Remedy: Steam inhalation, fluids, rest."
        )
    elif "headache" in user_input_lower:
        return (
            "🤕 Headache\n"
            "• Cause: Stress, dehydration, eye strain.\n"
            "• Prevention: Hydrate, sleep well.\n"
            "• Remedy: Rest, mild painkillers if needed."
        )
    else:
        return "I am here to help you with health-related questions."

def quantum_reply(user_input):
    try:
        expr = sp.sympify(user_input)
        simplified = sp.simplify(expr)
        return f"Simplified Result: {simplified}"
    except:
        if "=" in user_input:
            try:
                lhs, rhs = user_input.split("=")
                x = sp.symbols('x')
                eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
                sol = sp.solve(eq, x)
                return f"Solution: {sol}"
            except:
                return "Cannot solve this equation."
        return "I couldn't parse this math problem."

# ---------- CHAT INPUT ----------
user_input = st.text_input("Type your message here...", key="chat_input")

if user_input:
    # Add user message
    st.session_state.chat_history.append(("You", user_input))

    # Determine bot response
    if role == "Assistant":
        bot_response = f"{user_input}"  # direct response, no "You said"
    elif role == "AI Doctor":
        bot_response = doctor_reply(user_input)
    elif role == "Professor Quantum":
        bot_response = quantum_reply(user_input)
    else:
        bot_response = user_input

    # Add bot response
    st.session_state.chat_history.append((role, bot_response))

    # Speak automatically
    speak_text(bot_response)

# ---------- DISPLAY CHAT BELOW INPUT ----------
st.markdown("### Chat History")
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **{sender}:** {msg}")

# ---------- LIT HEART AT BOTTOM ----------
st.markdown(
    """
    <style>
    .lit-heart {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 25px;
        color: red;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: translateX(-50%) scale(1); }
        50% { transform: translateX(-50%) scale(1.2); }
        100% { transform: translateX(-50%) scale(1); }
    }
    </style>
    <div class="lit-heart">❤️</div>
    """,
    unsafe_allow_html=True
)


