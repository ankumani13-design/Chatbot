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

for msg in st.session_state.chat_history[1:]:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    st.sidebar.markdown(f"**{role}:** {msg['content']}")

# --- Sidebar: Settings ---
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
            sample_width=2,
            channels=1
        )
        audio_segment.export(audio_file, format="wav")
        audio_file.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return f"Error during recognition: {e}"

# --- Main Logic ---
if "text_buffer" not in st.session_state:
    st.session_state.text_buffer = ""

user_input = None

if input_mode == "Text Input" or input_mode == "Voice Input":
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input("Enter or edit your message here:", value=st.session_state.text_buffer, key="text_input")

    with col2:
        if input_mode == "Voice Input":
            if "audio_frames" not in st.session_state:
                st.session_state.audio_frames = []

            ctx = webrtc_streamer(
                key="voice-capture",
                mode=WebRtcMode.SENDONLY,
                audio_receiver_size=256,
                media_stream_constraints={"audio": True, "video": False},
            )

            if ctx.audio_receiver:
                try:
                    audio_frames = ctx.audio_receiver.get_frames(timeout=1)
                    if audio_frames:
                        st.session_state.audio_frames.extend([f.to_ndarray() for f in audio_frames])
                except:
                    pass  # timeout okay

            if st.button("🎤 Process Voice Input"):
                if st.session_state.audio_frames:
                    recognized_text = recognize_audio(st.session_state.audio_frames)
                    if recognized_text.startswith("Error"):
                        st.error(recognized_text)
                    else:
                        st.success(f"Recognized: {recognized_text}")
                        # Update input box with recognized text
                        st.session_state.text_buffer = recognized_text
                        st.experimental_rerun()  # Reload to show in text_input
                    st.session_state.audio_frames = []
                else:
                    st.warning("No audio captured yet.")

# --- GPT Processing ---
if user_input and user_input.strip():
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

    # Reset buffer after submission
    st.session_state.text_buffer = ""
    st.experimental_rerun()
