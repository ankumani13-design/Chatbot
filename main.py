import streamlit as st
import openai
from gtts import gTTS
import base64
import io
import speech_recognition as sr
from pydub import AudioSegment

# === SET YOUR OPENAI API KEY HERE ===
openai.api_key = "your-openai-api-key"

# Page config
st.set_page_config(page_title="GPT Voice/Text Chatbot", page_icon="🤖🎤")

st.title("🤖 GPT Voice/Text Chatbot with Voice Assistant Options")

# --- Sidebar: Settings ---
st.sidebar.header("Settings")

# Input mode selection
input_mode = st.sidebar.radio("Choose input mode:", ["Text Input", "Voice Upload"])

# Output language options for TTS
lang_options = {
    "en": "English",
    "en-au": "English (Australia)",
    "en-uk": "English (UK)",
    "en-us": "English (US)",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese"
}

output_lang = st.sidebar.selectbox("Voice Output Language:", list(lang_options.keys()), format_func=lambda k: lang_options[k])

# Voice assistant style (simulated by TTS language accent variants)
voice_styles = {
    "Default": output_lang,
    "Formal": "en-uk" if output_lang.startswith("en") else output_lang,
    "Casual": "en-au" if output_lang.startswith("en") else output_lang,
    "Friendly": "en-us" if output_lang.startswith("en") else output_lang,
}

voice_style = st.sidebar.selectbox("Voice Assistant Style:", list(voice_styles.keys()))

# Resolve actual language code for gTTS
tts_lang = voice_styles[voice_style]

# --- Session state for chat ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

# --- Helper Functions ---

def transcribe_audio(uploaded_file):
    try:
        audio = AudioSegment.from_file(uploaded_file)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            # Use default English recognition for transcription
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return f"Error during transcription: {e}"

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

def ask_gpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# --- Input UI ---

user_input = None

if input_mode == "Text Input":
    user_input = st.text_input("Type your message:")
else:
    uploaded_audio = st.file_uploader("Upload your voice (mp3 or wav):", type=["mp3", "wav"])
    if uploaded_audio is not None:
        with st.spinner("Transcribing audio..."):
            transcribed_text = transcribe_audio(uploaded_audio)
            if transcribed_text.startswith("Error"):
                st.error(transcribed_text)
            else:
                st.success(f"Transcribed: {transcribed_text}")
                user_input = transcribed_text

# --- Process input and chat ---

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("GPT is thinking..."):
        bot_response = ask_gpt(st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

    # Display conversation
    st.markdown(f"**You:** {user_input}")
    st.markdown(f"**Assistant:** {bot_response}")

    # Play TTS voice output
    audio_base64 = generate_tts_base64(bot_response, tts_lang)
    if audio_base64:
        st.markdown(
            f"""
            <audio autoplay controls style="display:none">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True,
        )

# --- Show full chat history ---
with st.expander("Show full chat history"):
    for msg in st.session_state.chat_history[1:]:
        role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{role}:** {msg['content']}")
