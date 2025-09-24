import streamlit as st
from gtts import gTTS
import base64
import wikipedia
import sympy as sp

# ---------- VOICE FUNCTION ----------
def speak_text(text, lang="en-us"):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
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
    except Exception as e:
        st.error(f"Voice error: {e}")

# ---------- QUANTUM REPLY FUNCTION ----------
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

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feature" not in st.session_state:
    st.session_state.feature = "Doctor Help"
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_link" not in st.session_state:
    st.session_state.last_link = None
if "last_bot_response" not in st.session_state:
    st.session_state.last_bot_response = ""
if "current_display_history" not in st.session_state:
    st.session_state.current_display_history = []
if "voice_lang" not in st.session_state:
    st.session_state.voice_lang = "en-us"  # default American English

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Settings")

    # Feature selector
    new_feature = st.radio(
        "Features",
        ("Doctor Help", "Quantum Solver", "Assistant")
    )
    if new_feature != st.session_state.feature:
        st.session_state.feature = new_feature
        st.session_state.current_display_history = []
        st.session_state.last_bot_response = ""
        st.session_state.last_image = None
        st.session_state.last_link = None

    st.divider()

    # Voice Language selector
    st.subheader("🎙️ Voice Language")
    lang_options = {
        "🇺🇸 English (US)": "en-us",
        "🇬🇧 English (UK)": "en-uk",
        "🇮🇳 English (India)": "en-in",
        "🇫🇷 French": "fr",
        "🇩🇪 German": "de",
        "🇮🇹 Italian": "it",
        "🇪🇸 Spanish": "es",
        "🇯🇵 Japanese": "ja",
        "🇰🇷 Korean": "ko",
        "🇨🇳 Chinese (Mandarin)": "zh-cn"
    }
    selected_lang = st.selectbox("Select Language", list(lang_options.keys()))
    st.session_state.voice_lang = lang_options[selected_lang]

    st.divider()
    st.header("📜 Chat History")
    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

# ---------- DYNAMIC PAGE TITLE ----------
page_titles = {
    "Doctor Help": "🤖 AI Doctor",
    "Quantum Solver": "🤖 Quantum Professor",
    "Assistant": "🤖 AI Assistant"
}
current_title = page_titles.get(st.session_state.feature, "🤖 AI Assistant")
st.set_page_config(page_title=current_title, page_icon="🤖", layout="wide")
st.title(current_title)

# ---------- DISPLAY CURRENT CHAT ----------
for sender, msg in st.session_state.current_display_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

# ---------- CHAT INPUT ----------
user_input = st.text_input("Type your message here...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.current_display_history.append(("You", user_input))
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

    elif st.session_state.feature == "Quantum Solver":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hi! I am your Quantum Professor. Ask me a math problem."
        else:
            bot_response = quantum_reply(user_input)

    elif st.session_state.feature == "Assistant":
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

    # Save response and speak
    st.session_state.chat_history.append(("Bot", bot_response))
    st.session_state.current_display_history.append(("Bot", bot_response))
    st.session_state.last_bot_response = bot_response
    speak_text(bot_response, lang=st.session_state.voice_lang)

# ---------- SHOW BOT RESPONSE BELOW INPUT ----------
if st.session_state.last_bot_response:
    st.markdown(f"**🤖 Bot:** {st.session_state.last_bot_response}")

# ---------- DISPLAY ASSISTANT IMAGE/LINK ----------
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
        font-size: 20px;
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
