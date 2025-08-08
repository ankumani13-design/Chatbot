import streamlit as st
import openai
from gtts import gTTS
import base64
import io
import speech_recognition as sr
from pydub import AudioSegment
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# === SET YOUR OPENAI API KEY HERE ===
openai.api_key = "your-openai-api-key"

# Page config
st.set_page_config(page_title="GPT Voice/Text Chatbot", page_icon="🤖🎤", layout="wide")

st.title("🤖 GPT Voice/Text Chatbot with Voice Assistant Options")

# --- Sidebar: Chat History ---
st.sidebar.header("Chat History")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

# Show chat history in sidebar
for msg in st.session_state.chat_history[1:]:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    st.sidebar.markdown(f"**{role}:** {msg['content']}")

# --- Sidebar: Settings ---
st.sidebar.header("Settings")

# Input mode selection
input_mode = st.sidebar.radio("Choose input mode:", ["Text Input", "Voice Input"])

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

# --- Helper Functions ---

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

def recognize_audio(frames):
    try:
        import numpy as np
        audio_np = np.concatenate(frames)
        audio_bytes = audio_np.tobytes()
        
        audio_file = io.BytesIO()
        audio_segment = AudioSegment(
            audio_bytes,
            frame_rate=48000,
            sample_width=2,  # int16 = 2 bytes
            channels=1
        )
        audio_segment.export(audio_file, format="wav")
        audio_file.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        return f"Error during recognition: {e}"

# --- Main Input UI ---

user_input = None

if input_mode == "Text Input":
    user_input = st.text_input("Type your message:")
else:
    st.info("Speak into your mic. When done, click 'Process Voice Input' to transcribe.")

    ctx = webrtc_streamer(
        key="voice-input",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        media_stream_constraints={"audio": True, "video": False},
    )

    if "audio_frames" not in st.session_state:
        st.session_state.audio_frames = []

    if ctx.audio_receiver:
        try:
            audio_frames = ctx.audio_receiver.get_frames(timeout=1)
            if audio_frames:
                st.session_state.audio_frames.extend([f.to_ndarray() for f in audio_frames])
        except:
            pass  # timeout errors ignored

    if st.button("Process Voice Input"):
        if st.session_state.audio_frames:
            recognized_text = recognize_audio(st.session_state.audio_frames)
            if recognized_text.startswith("Error"):
                st.error(recognized_text)
            else:
                st.success(f"Recognized: {recognized_text}")
                user_input = recognized_text
            st.session_state.audio_frames = []  # reset after processing
        else:
            st.warning("No audio captured yet. Please speak into the microphone.")

# --- Process input and chat ---

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("GPT is thinking..."):
        bot_response = ask_gpt(st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

    # Display conversation in main area
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
