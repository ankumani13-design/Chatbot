import streamlit as st
import wikipedia
from gtts import gTTS
import io
import base64
import speech_recognition as sr
from pydub import AudioSegment
from streamlit_audio_recorder import audio_recorder

# Page config
st.set_page_config(page_title="Wikipedia Voice Chatbot", page_icon="🎙️")
st.title("🎙️ Wikipedia Voice Chatbot with Mic, Text & Language Switch")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Supported languages (lang_code: language name)
language_options = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese"
}

# Language selection
selected_lang = st.selectbox("🌍 Choose language for response and voice:", options=list(language_options.keys()), format_func=lambda x: language_options[x])

# Wikipedia summary function
def get_wikipedia_summary(query, lang):
    try:
        wikipedia.set_lang(lang)
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

# Convert bot reply to speech
def text_to_speech_base64(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
        return audio_base64
    except Exception as e:
        return None

# Transcribe mic audio to text
def transcribe_audio(blob):
    try:
        audio = AudioSegment.from_file(io.BytesIO(blob), format="wav")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=selected_lang)
            return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        return "Speech recognition service is not available."
    except Exception as e:
        return f"Error: {str(e)}"

# Voice recorder
st.markdown("### 🎤 Record your question below")
audio_bytes = audio_recorder(text="Record", icon_size="2x", pause_threshold=1.5)

user_input = None

if audio_bytes:
    with st.spinner("Transcribing voice..."):
        recognized_text = transcribe_audio(audio_bytes)
        if recognized_text.startswith("Error") or "Sorry" in recognized_text:
            st.error(recognized_text)
        else:
            st.success(f"Recognized voice: {recognized_text}")
            user_input = recognized_text

# Text input
typed_input = st.text_input("Or type your question here:")

if typed_input:
    user_input = typed_input

# Process user input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_wikipedia_summary(user_input, selected_lang)
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Show conversation and voice reply
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
        if i == len(st.session_state.messages) - 1:
            audio_base64 = text_to_speech_base64(msg["content"], selected_lang)
            if audio_base64:
                audio_html = f"""
                    <audio autoplay controls style="display:none;">
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
