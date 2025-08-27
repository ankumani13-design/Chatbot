import streamlit as st
import wikipedia
import re
from gtts import gTTS
import os
import base64
from googletrans import Translator

translator = Translator()

# Function to create audio and autoplay
def autoplay_audio(text, lang_code="en"):
    tts = gTTS(text=text, lang=lang_code)
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    return f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """

# Function → fetch wikipedia info
def get_wikipedia_info(query, lang="en"):
    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(query, sentences=2)
        page = wikipedia.page(query)
        images = page.images[:1]
        return {"summary": summary, "url": page.url, "images": images}
    except:
        return {"summary": f"Sorry, I couldn't find details about {query}.", "url": None, "images": []}

# Function → process user input
def process_message(user_input):
    # Detect language
    detected = translator.detect(user_input)
    lang_code = detected.lang if detected.lang in ["en", "hi", "kn"] else "en"

    low = user_input.lower().strip()

    # Greetings
    if low in ["hi", "hello"]:
        reply = "Hello! How can I help you?" if lang_code == "en" else \
                "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?" if lang_code == "hi" else \
                "ಹಲೋ! ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
        return {"summary": reply, "url": None, "images": [], "lang": lang_code}

    if "how are you" in low or "how r u" in low:
        reply = "I am fine, how can I help you?" if lang_code == "en" else \
                "मैं ठीक हूँ, मैं आपकी कैसे मदद कर सकता हूँ?" if lang_code == "hi" else \
                "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ, ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
        return {"summary": reply, "url": None, "images": [], "lang": lang_code}

    # Math Solver
    try:
        if any(op in low for op in ["+", "-", "*", "/", "^"]):
            result = eval(low.replace("^", "**"))
            return {"summary": str(result), "url": None, "images": [], "lang": lang_code}
    except:
        pass

    # Doctor Mode → Fever Example
    if "fever" in low or "ಜ್ವರ" in low or "बुखार" in low:
        reply = {
            "en": "Fever can be caused by viral or bacterial infections. Drink fluids, take rest, and consult a doctor if it persists.",
            "hi": "बुखार वायरल या बैक्टीरियल संक्रमण से हो सकता है। तरल पदार्थ पिएं, आराम करें और यदि बना रहे तो डॉक्टर से संपर्क करें।",
            "kn": "ಜ್ವರ ವೈರಲ್ ಅಥವಾ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಸೋಂಕಿನಿಂದ ಉಂಟಾಗಬಹುದು. ದ್ರವಗಳನ್ನು ಕುಡಿಯಿರಿ, ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ, ಮುಂದುವರೆದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        }
        return {"summary": reply.get(lang_code, reply["en"]), 
                "url": "https://www.webmd.com/fever/fever-symptoms-causes", 
                "images": [], "lang": lang_code}

    # Default → Wikipedia search
    info = get_wikipedia_info(user_input, lang_code)
    info["lang"] = lang_code
    return info


# ------------------------------
# Streamlit UI
# ------------------------------
st.title("🌍 Multilingual AI Assistant")
st.write("Ask me anything in **English, Hindi, or Kannada**")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Type your message:")
if st.button("Send") and user_input:
    response = process_message(user_input)
    st.session_state.history.append(("🧑 You", user_input))
    st.session_state.history.append(("🤖 Bot", response["summary"]))

    # Show chat
    for sender, msg in st.session_state.history:
        st.markdown(f"**{sender}:** {msg}")

    # Show link
    if response["url"]:
        st.markdown(f"[More Info]({response['url']})")

    # Show images
    for img in response["images"]:
        st.image(img, width=300)

    # Voice reply (autoplay)
    st.markdown(autoplay_audio(response["summary"], response["lang"]), unsafe_allow_html=True)
