import streamlit as st
import wikipedia
from gtts import gTTS
import io

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

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

# User input
user_input = st.text_input("Ask me anything:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_wikipedia_summary(user_input)
    st.session_state.messages.append({"role": "bot", "content": bot_reply})

# Display messages and play voice on button click
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")
        if st.button("🔊 Play Voice", key=f"voice_{i}"):
            audio_data = text_to_speech(msg["content"])
            st.audio(audio_data, format="audio/mp3")
