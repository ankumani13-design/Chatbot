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

# ---------- APP CONFIG ----------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Assistant")

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {
        "Doctor Help": [],
        "Quantum Solver": [],
        "Assistant": []
    }
if "feature" not in st.session_state:
    st.session_state.feature = "Doctor Help"
if "active_feature" not in st.session_state:
    st.session_state.active_feature = "Doctor Help"
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_link" not in st.session_state:
    st.session_state.last_link = None

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Select Feature")
    new_feature = st.radio(
        "Features",
        ("Doctor Help", "Quantum Solver", "Assistant"),
        key="feature_radio"
    )

    st.markdown("---")
    st.subheader("📜 Chat History")
    for feat, chats in st.session_state.chat_history.items():
        if chats:
            st.markdown(f"**{feat}:**")
            for sender, msg in chats[-3:]:  # show last 3 messages
                st.markdown(f"- {sender}: {msg[:40]}...")

# Reset chat when switching features
if new_feature != st.session_state.active_feature:
    st.session_state.active_feature = new_feature
    st.session_state.last_image = None
    st.session_state.last_link = None
    st.session_state.chat_history[new_feature] = []  # clear on switch

st.session_state.feature = new_feature

# ---------- CHAT INPUT ----------
user_input = st.text_input("Type your message here...")

bot_response = None  # Initialize

if user_input:
    # Save user input
    st.session_state.chat_history[st.session_state.feature].append(("You", user_input))
    user_input_lower = user_input.lower()

    # ---------- FEATURE LOGIC ----------
    if st.session_state.feature == "Doctor Help":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hello! I am your personal AI doctor. How can I help you?"
        elif "fever" in user_input_lower:
            bot_response = (
                "🤒 **Fever**\n\n"
                "**Causes:** Viral or bacterial infections, flu, common cold.\n\n"
                "**Prevention:** Wash hands, maintain hygiene, stay hydrated.\n\n"
                "**Remedy:** Rest, drink fluids, take paracetamol if needed. "
                "Consult a doctor if fever persists or is above 102°F."
            )
        elif "cold" in user_input_lower:
            bot_response = (
                "🤧 **Cold**\n\n"
                "**Causes:** Viral infection of the respiratory tract.\n\n"
                "**Prevention:** Avoid contact with infected people, wash hands often.\n\n"
                "**Remedy:** Steam inhalation, warm fluids, vitamin C-rich foods."
            )
        elif "headache" in user_input_lower:
            bot_response = (
                "🤕 **Headache**\n\n"
                "**Causes:** Stress, dehydration, eye strain, lack of sleep.\n\n"
                "**Prevention:** Stay hydrated, reduce screen time, sleep 7–8 hours.\n\n"
                "**Remedy:** Rest, drink water, mild painkillers if needed."
            )
        else:
            bot_response = "I can assist you with common health issues like fever, cold, or headache."

    elif st.session_state.feature == "Quantum Solver":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Greetings! I am your AI Quantum Professor. What problem shall we solve today?"
        else:
            try:
                if "=" in user_input:
                    lhs, rhs = user_input.split("=")
                    x = symbols('x')
                    eq = Eq(parse_expr(lhs), parse_expr(rhs))
                    sol = solve(eq, x)
                    bot_response = (
                        f"🔬 **Quantum Solution Mode**\n\n"
                        f"Equation: {lhs} = {rhs}\n\n"
                        f"Mathematical Roots: {sol}\n\n"
                        f"In quantum terms, this represents a possible state collapse "
                        f"where `x` stabilizes into the given solution(s)."
                    )
                else:
                    expr = parse_expr(user_input_lower)
                    simplified = simplify(expr)
                    bot_response = (
                        f"🔬 **Quantum Simplification**\n\n"
                        f"Expression: {user_input}\n\n"
                        f"Result: {simplified}\n\n"
                        f"In quantum analogy, this is the reduced wavefunction of the system."
                    )
            except:
                bot_response = "I couldn't interpret the quantum equation. Try again with a valid expression."

    elif st.session_state.feature == "Assistant":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hello! I am your AI Assistant. Ask me about any topic."
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

    # Save bot response
    if bot_response:
        st.session_state.chat_history[st.session_state.feature].append(("Bot", bot_response))
        speak_text(bot_response)

# ---------- DISPLAY CHAT BELOW INPUT ----------
st.subheader("💬 Conversation")
for sender, msg in st.session_state.chat_history[st.session_state.feature]:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 {st.session_state.feature}:** {msg}")

# ---------- DISPLAY WIKI IMAGE/LINK ----------
if st.session_state.feature == "Assistant":
    if st.session_state.last_image:
        st.image(st.session_state.last_image, width=200)
    if st.session_state.last_link:
        st.markdown(f"[More Info 🔗]({st.session_state.last_link})")

# ---------- SMALL LIT HEART AT BOTTOM ----------
st.markdown(
    """
    <style>
    .lit-heart {
        position: fixed;
        bottom: 5px;
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
