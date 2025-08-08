import streamlit as st
import wikipedia
from gtts import gTTS
import io
import base64
import speech_recognition as sr
from pydub import AudioSegment

# Config
st.set_page_config(page_title="Wikipedia Voice Chatbot", page_icon="🎙️")
st.title("🎙️ Wikipedia Voice Chatbot")

# Language options
language_options = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese"
}

selected_lang = st.selectbox("🌍 Choose language:", list(language_options.keys()), format_func=lambda x: language_options[x])

# Get Wikipedia summary
def get_summary(query, lang):
    try:
        wikipedia.set_lang(lang)
        results = wikipedia.search(query)
        if not results:
            return "Sorry, I couldn't find anything on that topic."
        summary = wikipedia.summary(results[0], sentences=2)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"Did you mean: {', '.join(e.options[:5])}?"
    except:
        return "Something went wrong."

# Convert text to speech
def speak(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3 = io.BytesIO()
        tts.write_to_fp(mp3)
        mp3.seek(0)
        return base64.b64encode(mp3.read()).decode("utf-8")
    except:
        return None

# Transcribe uploaded audio
def transcribe(audio_file, lang):
    try:
        audio = AudioSegment.from_file(audio_file)
        wav = io.BytesIO()
        audio.export(wav, format="wav")
        wav.seek(0)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language=lang)
    except:
        return None

# User input
st.markdown("### 💬 Type your question:")
text_input = st.text_input("")

st.markdown("### 🎤 Or upload your voice (MP3 or WAV):")
audio_file = st.file_uploader("Upload voice", type=["mp3", "wav"])

user_query = None

if text_input:
    user_query = text_input
elif audio_file:
    with st.spinner("Transcribing..."):
        result = transcribe(audio_file, selected_lang)
        if result:
            st.success(f"Recognized: {result}")
            user_query = result
        else:
            st.error("Sorry, couldn't recognize the audio.")

# Show bot response
if user_query:
    st.markdown(f"**You:** {user_query}")
    reply = get_summary(user_query, selected_lang)
    st.markdown(f"**Bot:** {reply}")

    # Speak response
    audio_base64 = speak(reply, selected_lang)
    if audio_base64:
        st.markdown(
            f"""
            <audio autoplay controls style="display:none;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True
        )
