import streamlit as st
import wikipedia
from gtts import gTTS
import io
import base64

# --- Page Config ---
st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="wide")

# --- Custom CSS for white bg + black text ---
st.markdown(
    """
    <style>
        .stApp {
            background-color: white;
            color: black;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Title ---
st.title("🤖 Chatbot")

# --- Sidebar (Chat History + Features) ---
st.sidebar.header("📜 Chat History")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.sidebar.markdown(f"**{role}:** {msg['content']}")

# --- Sidebar Features ---
st.sidebar.header("⚡ Features")
feature = st.sidebar.radio(
    "Choose a domain:", 
    ["Wikipedia", "Medical", "Mathematics", "Science", "Arts"]
)

# --- Sidebar Language Selector ---
st.sidebar.header("🌍 Voice Language")
lang_options = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese"
}
voice_lang = st.sidebar.selectbox(
    "Choose language:", 
    list(lang_options.keys()), 
    format_func=lambda x: lang_options[x]
)

# --- Wikipedia Fetch Function ---
def get_wikipedia_summary(query):
    try:
        results = wikipedia.search(query)
        if not results:
            return "Sorry, I couldn't find anything on that topic."
        summary = wikipedia.summary(results[0], sentences=2, auto_suggest=False, redirect=True)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"Your query is ambiguous, did you mean: {', '.join(e.options[:5])}?"
    except wikipedia.PageError:
        return "Sorry, I couldn't find a page matching your query."
    except Exception:
        return "Oops, something went wrong."

# --- Text-to-Speech ---
def text_to_speech_base64(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode("utf-8")
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# --- User Input ---
user_input = st.text_input("💬 Ask me anything:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if feature == "Wikipedia":
        bot_reply = get_wikipedia_summary(user_input)

    elif feature == "Medical":
        bot_reply = get_wikipedia_summary(user_input + " medicine health disease anatomy")

    elif feature == "Mathematics":
        try:
            bot_reply = f"🧮 The answer is: {eval(user_input)}"
        except Exception:
            bot_reply = get_wikipedia_summary(user_input + " mathematics math formula")

    elif feature == "Science":
        bot_reply = get_wikipedia_summary(user_input + " science physics chemistry biology")

    elif feature == "Arts":
        bot_reply = get_wikipedia_summary(user_input + " art painting music literature")

    else:
        bot_reply = "Sorry, I don't know how to handle that yet."

    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# --- Display Messages & Voice Output ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {msg['content']}")

        # Generate speech for bot replies in chosen language
        audio_base64 = text_to_speech_base64(msg["content"], lang=voice_lang)
        if audio_base64:
            st.markdown(
                f"""
                <audio autoplay controls>
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                """,
                unsafe_allow_html=True,
            )

# --- Footer ---
st.markdown("---")
st.markdown("<h4 style='text-align: center;'>❤️ Made with love</h4>", unsafe_allow_html=True)
