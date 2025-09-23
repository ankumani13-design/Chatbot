import streamlit as st
from gtts import gTTS
import base64
import wikipedia
from sympy import symbols, Eq, solve, simplify
from sympy.parsing.sympy_parser import parse_expr

# ---------- VOICE FUNCTION ----------
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

# ---------- APP CONFIG ----------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Assistant")

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feature" not in st.session_state:
    st.session_state.feature = "Doctor Help"
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_link" not in st.session_state:
    st.session_state.last_link = None

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Select Feature")
    st.session_state.feature = st.radio(
        "Features",
        ("Doctor Help", "Math Solver", "Wikipedia")
    )
    st.divider()
    st.header("📜 Chat History")
    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

# ---------- DISPLAY CHAT HISTORY ----------
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

# ---------- CHAT INPUT ----------
user_input = st.text_input("Type your message here...")

if user_input:
    # Save user message
    st.session_state.chat_history.append(("You", user_input))
    user_input_lower = user_input.lower()
    bot_response = ""

    # ---------- FEATURE LOGIC ----------
    if st.session_state.feature == "Doctor Help":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hello! I am your personal AI doctor. How can I help you?"
        elif "fever" in user_input_lower:
            bot_response = (
                "🤒 Fever\n"
                "• Cause: Usually due to infections like flu or cold.\n"
                "• Prevention: Stay hydrated, rest, maintain hygiene.\n"
                "• Remedy: Take paracetamol and consult a doctor if high fever persists."
            )
        elif "cold" in user_input_lower:
            bot_response = (
                "🤧 Cold\n"
                "• Cause: Viral infection of upper respiratory tract.\n"
                "• Prevention: Wash hands, maintain warm environment.\n"
                "• Remedy: Steam inhalation, warm fluids, rest well."
            )
        elif "headache" in user_input_lower:
            bot_response = (
                "🤕 Headache\n"
                "• Cause: Stress, dehydration, eye strain, migraine.\n"
                "• Prevention: Hydrate, sleep well, avoid excessive screens.\n"
                "• Remedy: Rest, hydration, mild painkillers if needed."
            )
        else:
            bot_response = "I am here to help you with health-related questions."

    elif st.session_state.feature == "Math Solver":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hi! I am your AI professor. How can I help you today?"
        else:
            try:
                expr = parse_expr(user_input_lower)
                simplified = simplify(expr)
                bot_response = f"✅ Simplified Result: {simplified}"
            except:
                try:
                    if "=" in user_input:
                        lhs, rhs = user_input.split("=")
                        x = symbols('x')
                        eq = Eq(parse_expr(lhs), parse_expr(rhs))
                        sol = solve(eq, x)
                        bot_response = f"✅ Solution: {sol}"
                    else:
                        bot_response = "Invalid math expression."
                except:
                    bot_response = "I couldn't parse the math problem."

    elif st.session_state.feature == "Wikipedia":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hello! Ask me about any topic and I will fetch info from Wikipedia."
            st.session_state.last_image = None
            st.session_state.last_link = None
        else:
            try:
                summary = wikipedia.summary(user_input, sentences=2)
                page = wikipedia.page(user_input)
                bot_response = summary
                st.session_state.last_image = page.images[0] if page.images else None
                st.session_state.last_link = page.url
            except:
                bot_response = "Sorry, I couldn't find information on that topic."
                st.session_state.last_image = None
                st.session_state.last_link = None

    # Save bot response and autoplay voice
    st.session_state.chat_history.append(("Bot", bot_response))
    speak_text(bot_response)

# ---------- DISPLAY WIKI IMAGE/LINK ----------
if st.session_state.feature == "Wikipedia":
    if st.session_state.last_image:
        st.image(st.session_state.last_image, width=200)
    if st.session_state.last_link:
        st.markdown(f"[More Info 🔗]({st.session_state.last_link})")

# ---------- LIT HEART AT BOTTOM ----------
st.markdown(
    """
    <style>
    .lit-heart {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 40px;
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
