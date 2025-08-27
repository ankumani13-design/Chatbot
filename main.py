import streamlit as st
import wikipedia
import webbrowser
from gtts import gTTS
import base64
from deep_translator import GoogleTranslator

# Page config
st.set_page_config(page_title="AI Assistant", layout="wide")

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Function: Convert text to speech (autoplay)
def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("voice.mp3")
    with open("voice.mp3", "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# Function: Handle queries
def get_response(user_input):
    user_input = user_input.lower()

    # Small talk
    if "how are you" in user_input:
        return "I am fine, how can I help you?"

    # Math
    if "*" in user_input or "+" in user_input or "-" in user_input or "/" in user_input:
        try:
            result = eval(user_input)
            return f"The answer is {result}"
        except:
            return "Sorry, I couldn't solve that."

    # Health
    if "fever" in user_input:
        return ("Causes: Infection, flu, etc.\n"
                "Prevention: Rest, hydration, avoid cold foods.\n"
                "Prescription: Take paracetamol, consult a doctor if high fever continues.")

    # Open Google
    if "open google" in user_input:
        webbrowser.open("https://www.google.com")
        return "Opening Google..."

    # Wikipedia search
    try:
        summary = wikipedia.summary(user_input, sentences=2)
        page = wikipedia.page(user_input)
        img_url = page.images[0] if page.images else None
        link = page.url
        result = summary
        if img_url:
            st.image(img_url, caption=user_input.title(), width=300)
        st.markdown(f"[Click here for more details]({link})")
        return result
    except:
        return "Sorry, I couldn't find information on that."

# UI
st.title("🤖 AI Assistant")

# Show chat history on left
for role, msg in st.session_state.history:
    align = "left" if role == "user" else "right"
    st.markdown(f"<div style='text-align: {align};'><b>{role.capitalize()}:</b> {msg}</div>", unsafe_allow_html=True)

# Input box
user_input = st.text_input("Type your message here...")

if user_input:
    # Get response
    response = get_response(user_input)

    # Save to history
    st.session_state.history.append(("user", user_input))
    st.session_state.history.append(("bot", response))

    # Show immediately
    st.experimental_rerun()

# Voice output for last bot response
if st.session_state.history and st.session_state.history[-1][0] == "bot":
    speak(st.session_state.history[-1][1])

# Footer with heart
st.markdown("<h4 style='text-align: center;'>❤️</h4>", unsafe_allow_html=True)
