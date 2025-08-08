import streamlit as st
from gtts import gTTS
import base64
import io
import speech_recognition as sr
from pydub import AudioSegment
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np

# --- Page Setup ---
st.set_page_config(page_title="Offline Voice/Text Bot", page_icon="🎤", layout="wide")
st.title("🎤 Offline Voice/Text Chatbot with Voice Output")

# --- Chat History ---
st.sidebar.header("Chat History")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    st.sidebar.markdown(f"**{role}:** {msg['content']}")

# --- Settings ---
st.sidebar.header("Settings")

input_mode = st.sidebar.radio("Choose input mode:", ["Text Input", "Voice Input"])

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

# --- TTS Generator ---
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

# --- Voice Recognition ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.frames = []

    def recv(self, frame):
        audio = frame.to_ndarray(format="int16")
        self.frames.append(audio)
        return frame

def recognize_audio(frames):
    try:
        audio_np = np.concatenate(frames)
        audio_bytes = audio_np.tobytes()
        audio_file = io.BytesIO()
        audio_segment = AudioSegment(
            audio_bytes,
            frame_rate=48000,
            sample_width=2,
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

# --- Input UI ---
user_input = None

if input_mode == "Text Input":
    user_input = st.text_input("Type your message:", key="text_input")
else:
    st.info("🎙 Speak into your mic, then click '🎧 Process Voice Input'")
    ctx = webrtc_streamer(
        key="voice",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_receiver:
        if st.button("🎧 Process Voice Input"):
            audio_frames = []
            try:
                audio_frame = ctx.audio_receiver.get_frames(timeout=3)
                audio_frames.extend([f.to_ndarray() for f in audio_frame])
            except:
                st.warning("No audio detected.")
            if audio_frames:
                result = recognize_audio(audio_frames)
                if result.startswith("Error"):
                    st.error(result)
                else:
                    st.success(f"Recognized: {result}")
                    user_input = result

# --- Output (TTS only) ---
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.markdown(f"**You:** {user_input}")

    # Voice reply (repeating the message)
    audio_base64 = generate_tts_base64(user_input, tts_lang)
    if audio_base64:
        st.markdown(
            f"""
            <audio autoplay style="display:none">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.chat_history.append({"role": "assistant", "content": user_input})
