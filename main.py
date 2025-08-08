import streamlit as st
import wikipedia
from gtts import gTTS
import io
import base64
import speech_recognition as sr
from pydub import AudioSegment

# Page config
st.set_page_config(page_title="Wikipedia Voice Chatbot", page_icon="🎙️")
st.title("🎙️ Wikipedia Voice Chatbot with Text, File Upload & Language Switching")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Supported languages
language_options = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese"
}

selected_lang = st.selectbox("🌐 Choose language:", list(language_options.keys()), format_func=lambda x: language_options[x])

# Wikipedia summary
def get_wikipedia_summary(query, lang):
    try:
        wikipedia.set_lang(lang)
        results = wikipedia.search(query)
        if not results:
            return "Sorry, I couldn't find anything on that topic."
        summary = wikipedia.summary(results[0], sentences=2, auto_suggest=False, redirect=True)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"Your query is ambiguous. Did you mean: {', '.join(e.options[:5])}?"
    except wikipedia.PageError:
        return "Sorry, I couldn't find a page matching your query."
    except Exception:
        return "Oops, something went wrong."

# Text-to-speech
def text_to_speech_base64(text, lang):
    tts = gTTS(text=text, lang=lang)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
    return audio_base64

# Transcribe uploaded audio
def transcribe_audio(uploaded_file, lang_code):
    try:
        audio = AudioSegment.from_file(uploaded_file)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=lang_code)
            return text
    except Exception as e:
        return f"Error: {str(e)}"

# File upload for voice input
st.markdown("### 🎤 Upload your voice (MP3/WAV):")
voice_file = st.file_uploader("Upload audio", type=["wav", "mp3"])

user_input = None

if voice_file:
    with st.spinner("Transcribing voice..."):
        user_input = transcribe_audio(voice_file, selected_lang)
        if user_input.startswith("Error"):
            st.error(user_input)
            user_input = None
        else:
            st.success(f"Recognized: {user_input}")

# Text input fallback
typed_input = st.text_input("💬 Or type your question here:")

if typed_input:
    user_input = typed_input

# Process input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_wikipedia_summary(user_input, selected_lang)
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display conversation
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
        if i == len(st.session_state.messages) - 1:
            audio_base64 = text_to_speech_base64(msg["content"], selected_lang)
            audio_html = f"""
                <audio autoplay controls style="display:none;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
