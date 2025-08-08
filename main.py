import streamlit as st
import openai
from gtts import gTTS
import base64
import io
from pydub import AudioSegment
import speech_recognition as sr

# Page config
st.set_page_config(page_title="GPT Voice Chatbot", page_icon="🎤")
st.title("🧠 GPT Voice Chatbot with Text & Voice")

# Sidebar settings
st.sidebar.title("🔐 API & Language Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
language = st.sidebar.selectbox("🌐 Voice Output Language", {
    "en": "English", "hi": "Hindi", "es": "Spanish", 
    "fr": "French", "de": "German", "ja": "Japanese"
})

if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

openai.api_key = api_key

# Session state for conversation
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Transcribe voice input
def transcribe_audio(blob):
    try:
        audio = AudioSegment.from_file(blob)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return f"Could not transcribe audio: {e}"

# Text to speech (gTTS)
def speak_text(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode("utf-8")
    except:
        return None

# Chat with GPT
def get_gpt_reply(user_input):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.chat_history
    )
    reply = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    return reply

# Input section
st.subheader("🎙️ Speak or Type Your Message")

user_input = None

# Live voice recording (Streamlit mic input)
audio_input = st.audio(label="🎧 Record your voice or upload MP3/WAV", format="audio/wav")
uploaded_audio = st.file_uploader("Or upload an audio file", type=["mp3", "wav"])

if uploaded_audio:
    with st.spinner("Transcribing uploaded audio..."):
        user_input = transcribe_audio(uploaded_audio)
        if "Could not" not in user_input:
            st.success(f"🗣️ You said: {user_input}")
        else:
            st.error(user_input)
elif audio_input:
    st.info("Voice input playback only — upload a file for transcription.")

typed_text = st.text_input("✍️ Or type your question here:")

if typed_text:
    user_input = typed_text

# Process and display GPT response
if user_input:
    with st.spinner("🤖 Thinking..."):
        bot_response = get_gpt_reply(user_input)

    st.markdown(f"**🧑 You:** {user_input}")
    st.markdown(f"**🤖 GPT:** {bot_response}")

    # Voice output
    tts_base64 = speak_text(bot_response, lang=language)
    if tts_base64:
        st.markdown(
            f"""
            <audio autoplay controls style="display:none;">
                <source src="data:audio/mp3;base64,{tts_base64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True
        )

# Chat history
with st.expander("🕘 Show Chat History"):
    for msg in st.session_state.chat_history[1:]:
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")
