import streamlit as st
import wikipedia
from gtts import gTTS
import io
import base64

# Page config
st.set_page_config(page_title="Wikipedia Chatbot", page_icon="📚")
st.title("📚 Wikipedia Chatbot with Voice Output")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to fetch summary from Wikipedia
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

# Function to convert text to speech and return audio as base64
def text_to_speech_base64(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
    return audio_base64

# User input
user_input = st.text_input("Ask me anything:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_wikipedia_summary(user_input)
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display messages and auto play bot response
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
        
        # Auto play voice for the latest bot response only
        if i == len(st.session_state.messages) - 1:
            audio_base64 = text_to_speech_base64(msg["content"])
            audio_html = f"""
                <audio autoplay controls style="display:none;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
