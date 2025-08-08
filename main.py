import streamlit as st
import wikipedia
from gtts import gTTS
import io
import base64
import speech_recognition as sr
from pydub import AudioSegment

# Page config
st.set_page_config(page_title="Wikipedia Voice Chatbot", page_icon="🎙️")
st.title("🎙️ Wikipedia Voice Chatbot with Auto Voice Reply")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wikipedia summary
def get_wikipedia_summary(query):
    try:
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

# Text to speech
def text_to_speech_base64(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
    return audio_base64

# Voice input using file uploader
st.markdown("### 🎤 Record or Upload Your Voice")
audio_file = st.file_uploader("Upload your voice (WAV/MP3)", type=["wav", "mp3"])

user_input = None

if audio_file is not None:
    # Convert uploaded audio to WAV if needed
    audio = AudioSegment.from_file(audio_file)
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    # Use speech recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_io) as source:
        audio_data = recognizer.record(source)
        try:
            user_input = recognizer.recognize_google(audio_data)
            st.success(f"Recognized Text: {user_input}")
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError:
            st.error("Speech Recognition service is unavailable.")

# Or fallback to text input
text_input = st.text_input("Or type your question below:")

if text_input:
    user_input = text_input

# Process user input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_wikipedia_summary(user_input)
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display conversation and auto play bot response
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
        if i == len(st.session_state.messages) - 1:
            audio_base64 = text_to_speech_base64(msg["content"])
            audio_html = f"""
                <audio autoplay controls style="display:none;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
