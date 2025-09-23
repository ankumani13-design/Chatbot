import streamlit as st
from gtts import gTTS
import base64

# ---------- VOICE FUNCTION ----------
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    file_path = "voice.mp3"
    tts.save(file_path)

    # Read the file and convert to base64
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()

    # Inject autoplay audio player
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ---------- APP CONFIG ----------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Assistant")

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("📜 Chat History")
    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

    st.divider()
    st.header("➕ Quick Maths Solver")
    math_input = st.text_input("Enter expression (e.g., 2*3)", key="math_input")
    if st.button("Solve Math"):
        try:
            result = eval(math_input)
            st.success(f"Answer: {result}")
        except:
            st.error("Invalid expression")

    st.divider()
    st.header("🏥 Doctor Help")
    st.info("Try typing 'fever', 'cold', or 'headache' in chat")

# ---------- CHAT INPUT ----------
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    # Save user message
    st.session_state.chat_history.append(("You", user_input))

    # ---------- BOT RESPONSE ----------
    user_input_lower = user_input.lower()
    if "hi" in user_input_lower:
        bot_response = "Hello buddy! How can I help you today?"
    elif "*" in user_input_lower or "+" in user_input_lower or "-" in user_input_lower or "/" in user_input_lower:
        try:
            result = eval(user_input_lower)
            bot_response = f"The answer is {result}"
        except:
            bot_response = "I couldn't calculate that."
    elif "fever" in user_input_lower:
        bot_response = "🤒 Fever Tip: Drink fluids, rest, take paracetamol if needed. See a doctor if persistent."
    elif "cold" in user_input_lower:
        bot_response = "🤧 Cold Tip: Drink warm fluids, use steam inhalation, rest well. See a doctor if severe."
    elif "headache" in user_input_lower:
        bot_response = "🤕 Headache Tip: Rest, stay hydrated, avoid screen time. Consult a doctor if persistent."
    else:
        bot_response = f"You said: {user_input}"

    # Save bot response
    st.session_state.chat_history.append(("Bot", bot_response))

    # Speak out the bot response (autoplay)
    speak_text(bot_response)

# ---------- DISPLAY CHAT HISTORY ----------
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
