import streamlit as st
import wikipedia
from gtts import gTTS
import io
import base64

# Page config
st.set_page_config(page_title="Chatbot", page_icon="❤️")
st.title("🤖 Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to fetch Wikipedia summary + image + link
def get_wikipedia_info(query):
    try:
        page = wikipedia.page(query, auto_suggest=False, redirect=True)
        summary = wikipedia.summary(query, sentences=2, auto_suggest=False, redirect=True)
        return {
            "summary": summary,
            "url": page.url,
            "images": page.images[:1]  # first image only
        }
    except Exception:
        return {
            "summary": "Sorry, I couldn't find details on that topic.",
            "url": None,
            "images": []
        }

# Function to convert text to speech (autoplay)
def text_to_speech_auto(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_bytes = mp3_fp.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# Function to handle conversation
def process_message(user_input):
    low = user_input.lower().strip()

    # Special commands
    if low == "hi":
        return {"summary": "Hello! How can I help you?", "url": None, "images": []}

    if low in ["how are you", "how r u", "how are u"]:
        return {"summary": "I am fine, how can I help you?", "url": None, "images": []}

    if low == "open google":
        st.markdown(
            """
            <script>
            window.open("https://www.google.com", "_blank").focus();
            </script>
            """,
            unsafe_allow_html=True,
        )
        return {"summary": "Opening Google in a new tab...", "url": None, "images": []}

    # Default → fetch Wikipedia info
    return get_wikipedia_info(user_input)

# Chat input
user_input = st.text_input("Type your message:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = process_message(user_input)
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display conversation (left-aligned chat style)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"🧑 **You:** {msg['content']}", unsafe_allow_html=True)
    else:
        if msg["content"]["summary"]:
            st.markdown(f"🤖 **Bot:** {msg['content']['summary']}", unsafe_allow_html=True)
            text_to_speech_auto(msg["content"]["summary"])  # autoplay voice

        if msg["content"]["images"]:
            st.image(msg["content"]["images"][0], width=300)

        if msg["content"]["url"]:
            st.markdown(f"[🔗 More info]({msg['content']['url']})")

# Heart at the bottom
st.markdown("<h3 style='text-align: center;'>❤️</h3>", unsafe_allow_html=True)
