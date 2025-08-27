import streamlit as st
from gtts import gTTS
import base64
import io
import wikipedia
import sympy as sp

# --- Page Setup ---
st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="wide")

# --- Custom CSS for background + text ---
st.markdown(
    """
    <style>
        body { background-color: white; color: black; }
        .stMarkdown { color: black; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Chatbot")

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar history
st.sidebar.header("🕑 Chat History")
for msg in st.session_state.chat_history:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    st.sidebar.markdown(f"**{role}:** {msg['content']}")

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")

features = st.sidebar.multiselect(
    "Select Features:",
    ["Wikipedia", "Medical", "Mathematics", "Science", "Arts"],
    default=["Wikipedia"]
)

lang_options = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "ja": "Japanese"
}
tts_lang = st.sidebar.selectbox(
    "Voice Output Language:",
    list(lang_options.keys()),
    format_func=lambda k: lang_options[k]
)

# --- TTS Generator ---
def generate_tts_base64(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode("utf-8")
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# --- Chat Input ---
user_input = st.text_input("💬 Type your message here:")

# --- Main Logic ---
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = "I am not sure how to respond."
    try:
        if "Mathematics" in features:
            try:
                expr = sp.sympify(user_input)
                result = sp.simplify(expr)
                response = f"Mathematics result: {result}"
            except:
                response = "Could not solve that math expression."

        elif "Wikipedia" in features:
            response = wikipedia.summary(user_input, sentences=2)

        elif "Medical" in features:
            response = "🩺 Medical feature placeholder. (Future expansion)"

        elif "Science" in features:
            response = "🔬 Science feature placeholder. (Future expansion)"

        elif "Arts" in features:
            response = "🎭 Arts feature placeholder. (Future expansion)"

    except Exception as e:
        response = f"Error: {e}"

    # Display conversation
    st.markdown(f"**🧑 You:** {user_input}")
    st.markdown(f"**🤖 Chatbot:** {response}")

    # Save to history
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Voice reply
    audio_base64 = generate_tts_base64(response, tts_lang)
    if audio_base64:
        st.markdown(
            f"""
            <audio autoplay style="display:none">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True,
        )

# --- Show All Chats on Main Page ---
st.markdown("## 📝 Conversation History")
for msg in st.session_state.chat_history:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Chatbot"
    st.markdown(f"**{role}:** {msg['content']}")

# --- Footer ---
st.markdown("<center>❤️ Built with Love</center>", unsafe_allow_html=True)
