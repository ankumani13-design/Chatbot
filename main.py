import streamlit as st
import wikipedia
import requests
from gtts import gTTS
from io import BytesIO
import base64
from PIL import Image
from bs4 import BeautifulSoup

st.set_page_config(page_title="🤖 AI Assistant", page_icon="🤖", layout="centered")

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Function: Text-to-Speech
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    return audio_html

# Function: Get Wikipedia info with image
def get_wiki_info(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        page = wikipedia.page(query)
        image_url = page.images[0] if page.images else None
        return summary, image_url, page.url
    except:
        return "Sorry, I couldn't fetch info for that.", None, None

# Function: Special Features
def handle_features(user_input):
    user_input_lower = user_input.lower()

    if user_input_lower == "hi":
        return "Hello, how can I help you today?", None, None

    if user_input_lower == "how are you":
        return "I am fine, how can I help you?", None, None

    if "open google" in user_input_lower:
        st.markdown("[Click here to open Google 🌐](https://www.google.com)")
        return "Opening Google...", None, "https://www.google.com"

    if "*" in user_input_lower or "+" in user_input_lower or "-" in user_input_lower or "/" in user_input_lower:
        try:
            result = eval(user_input_lower)
            return f"The answer is {result}", None, None
        except:
            return "I couldn't calculate that.", None, None

    if "fever" in user_input_lower:
        return ("Fever is usually caused by infections. "
                "Prevention: stay hydrated, rest, and take paracetamol if needed. "
                "Consult a doctor if it persists."), None, None

    # Otherwise Wikipedia
    return get_wiki_info(user_input)

# UI
st.title("🤖 AI Assistant")

for chat in st.session_state.history:
    st.markdown(f"**You:** {chat['user']}")
    st.markdown(f"**Bot:** {chat['bot']}")
    if chat["audio"]:
        st.markdown(chat["audio"], unsafe_allow_html=True)
    if chat["image"]:
        st.image(chat["image"], width=200)
    if chat["link"]:
        st.markdown(f"[More Info 🔗]({chat['link']})")

user_input = st.text_input("Type your message here...")

if st.button("Send") and user_input:
    response, image_url, link = handle_features(user_input)
    audio_html = speak_text(response)

    chat_entry = {
        "user": user_input,
        "bot": response,
        "audio": audio_html,
        "image": image_url,
        "link": link
    }
    st.session_state.history.append(chat_entry)
    st.experimental_rerun()
