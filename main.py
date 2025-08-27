import streamlit as st
import wikipedia
from gtts import gTTS
from io import BytesIO
import base64
from PIL import Image

st.set_page_config(page_title="🤖 AI Assistant", page_icon="🤖", layout="wide")

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Function: Text-to-Speech
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    return audio_html

# Function: Get Wikipedia info with image
def get_wiki_info(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        page = wikipedia.page(query)
        image_url = page.images[0] if page.images else None
        return summary, image_url, page.url
    except:
        return "Sorry, I couldn't fetch info for that.", None, None

# Function: Special Features
def handle_features(user_input):
    user_input_lower = user_input.lower()

    if user_input_lower == "hi":
        return "Hello, how can I help you today?", None, None

    if user_input_lower == "how are you":
        return "I am fine, how can I help you?", None, None

    if "open google" in user_input_lower:
        st.markdown("[Click here to open Google 🌐](https://www.google.com)")
        return "Opening Google...", None, "https://www.google.com"

    # Math solver
    if any(op in user_input_lower for op in ["+", "-", "*", "/", "**"]):
        try:
            result = eval(user_input_lower)
            return f"The answer is {result}", None, None
        except:
            return "I couldn't calculate that.", None, None

    # Doctor help
    if "fever" in user_input_lower:
        return ("🤒 Fever Tip: Drink fluids, rest, and take paracetamol if needed. "
                "See a doctor if it lasts >3 days."), None, None

    if "cold" in user_input_lower:
        return ("🤧 Cold Tip: Drink warm fluids, use steam inhalation, "
                "and rest well. Consult a doctor if severe."), None, None

    if "headache" in user_input_lower:
        return ("🤕 Headache Tip: Rest, stay hydrated, avoid screen time. "
                "If persistent, check with a doctor."), None, None

    # Default Wikipedia
    return get_wiki_info(user_input)


# ---------- UI Layout ----------
st.title("🤖 AI Assistant")

# Sidebar (Chat History + Quick Tools)
with st.sidebar:
    st.header("📜 Chat History")
    for i, chat in enumerate(st.session_state.history, 1):
        st.markdown(f"**{i}. You:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")

    st.divider()
    st.header("➕ Quick Maths")
    math_query = st.text_input("Enter expression (e.g., 5*5)", key="math")
    if st.button("Solve"):
        try:
            result = eval(math_query)
            st.success(f"Answer: {result}")
        except:
            st.error("Invalid Expression")

    st.divider()
    st.header("🏥 Doctor Help")
    st.info("Try typing: 'fever', 'cold', 'headache' in chat")

# Main chat area
user_input = st.text_input("Type your message here...")

if st.button("Send") and user_input:
    response, image_url, link = handle_features(user_input)
    audio_html = speak_text(response)

    chat_entry = {
        "user": user_input,
        "bot": response,
        "audio": audio_html,
        "image": image_url,
        "link": link
    }
    st.session_state.history.append(chat_entry)
    st.experimental_rerun()

# Display last response
if st.session_state.history:
    last = st.session_state.history[-1]
    st.markdown(f"**You:** {last['user']}")
    st.markdown(f"**Bot:** {last['bot']}")
    if last["audio"]:
        st.markdown(last["audio"], unsafe_allow_html=True)
    if last["image"]:
        st.image(last["image"], width=200)
    if last["link"]:
        st.markdown(f"[More Info 🔗]({last['link']})")
