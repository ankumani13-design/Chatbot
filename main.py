import streamlit as st
import wikipedia
from transformers import pipeline, Conversation
from gtts import gTTS
import base64
import io

# Load chatbot model
chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

st.set_page_config(page_title="Chatbot", page_icon="❤️", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    body {
        background-color: white;
        color: black;
    }
    .stTextInput > div > div > input {
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Chatbot")

# Session state to store chat
if "history" not in st.session_state:
    st.session_state.history = []

# Function: Text to Speech (auto-play)
def text_to_speech(text):
    tts = gTTS(text=text, lang="en")
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_bytes = mp3_fp.read()
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# Function: Wikipedia summary
def get_wikipedia_summary(query):
    try:
        results = wikipedia.search(query)
        if results:
            return wikipedia.summary(results[0], sentences=2)
    except:
        return None
    return None

# Function: Math solver
def solve_math(query):
    try:
        result = eval(query, {"__builtins__": {}})
        return f"The answer is {result}"
    except:
        return None

# User input
user_input = st.text_input("💬 You:")

if user_input:
    # Try Math
    bot_reply = solve_math(user_input)

    # Try Wikipedia
    if bot_reply is None:
        bot_reply = get_wikipedia_summary(user_input)

    # Fallback: Conversation model
    if bot_reply is None:
        conv = Conversation(user_input)
        result = chatbot(conv)
        bot_reply = result.generated_responses[-1]

    # Save chat history
    st.session_state.history.append(("You", user_input))
    st.session_state.history.append(("Bot", bot_reply))

    # Speak reply
    text_to_speech(bot_reply)

# Display conversation
for role, msg in st.session_state.history:
    st.markdown(f"**{role}:** {msg}")

# Heart at the bottom
st.markdown("<h3 style='text-align: center;'>❤️</h3>", unsafe_allow_html=True)
