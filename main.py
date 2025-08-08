import streamlit as st
import openai
from gtts import gTTS
import base64
import io
import speech_recognition as sr
from pydub import AudioSegment
from streamlit_audio_recorder import audio_recorder

# === SET YOUR OPENAI API KEY HERE ===
openai.api_key = "your-openai-api-key"

st.set_page_config(page_title="GPT Voice/Text Chatbot", page_icon="🤖🎤")
st.title("🤖 GPT Voice/Text Chatbot with Live Voice Input")

# Sidebar settings
st.sidebar.header("Settings")

input_mode = st.sidebar.radio("Choose input mode:", ["Text Input", "Voice Recording"])

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

voice_styles = {
    "Default": output_lang,
    "Formal": "en-uk" if output_lang.startswith("en") else output_lang,
    "Casual": "en-au" if output_lang.startswith("en") else output_lang,
    "Friendly": "en-us" if output_lang.startswith("en") else output_lang,
}

voice_style = st.sidebar.selectbox("Voice Assistant Style:", list(voice_styles.keys()))
tts_lang = voice_styles[voice_style]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

def transcribe_audio_blob(blob_bytes):
    try:
        audio = AudioSegment.from_file(io.BytesIO(blob_bytes), format="wav")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            # Recognize with Google Speech Recognition (default English)
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

user_input = None

if input_mode == "Text Input":
    user_input = st.text_input("Type your message:")
else:
    st.markdown("### 🎙️ Record your question (click record, speak, then stop)")
    audio_bytes = audio_recorder(text="Record", pause_threshold=1.5, icon_size="2x")
    if audio_bytes:
        with st.spinner("Transcribing audio..."):
            recognized_text = transcribe_audio_blob(audio_bytes)
            if recognized_text.startswith("Error"):
                st.error(recognized_text)
            else:
                st.success(f"Recognized: {recognized_text}")
                user_input = recognized_text

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("GPT is thinking..."):
        bot_response = ask_gpt(st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

    st.markdown(f"**You:** {user_input}")
    st.markdown(f"**Assistant:** {bot_response}")

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

with st.expander("Show full chat history"):
    for msg in st.session_state.chat_history[1:]:
        role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
        st.markdown(f"**{role}:** {msg['content']}")
