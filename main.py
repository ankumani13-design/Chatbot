import streamlit as st
from gtts import gTTS
import base64
import wikipedia
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.physics.quantum import Dagger
from sympy import symbols, Eq, solve, simplify

# ---------- VOICE FUNCTION ----------
def speak_text(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        file_path = "voice.mp3"
        tts.save(file_path)
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Voice error: {e}")

# ---------- DISEASE DATABASE ----------
disease_data = {
    # Minor Diseases
    "cold": {"severity":"Minor","cause":"Viral infection of the upper respiratory tract.","symptoms":"Sneezing, runny nose, mild fever, sore throat.","prevention":"Wash hands, avoid cold exposure, stay warm.","remedy":"Steam inhalation, rest, warm fluids."},
    "headache": {"severity":"Minor","cause":"Stress, dehydration, migraine.","symptoms":"Pain in head, sensitivity to light, nausea.","prevention":"Hydration, sleep well, reduce stress.","remedy":"Hydration, rest, mild painkillers."},
    "fever": {"severity":"Minor","cause":"Often viral or bacterial infections.","symptoms":"High body temperature, chills, body ache.","prevention":"Maintain hygiene, stay hydrated.","remedy":"Paracetamol, rest, consult doctor if persistent."},
    "sore throat": {"severity":"Minor","cause":"Viral or bacterial infection.","symptoms":"Painful throat, difficulty swallowing.","prevention":"Avoid cold drinks, wash hands.","remedy":"Warm salt water gargle, rest."},
    "cough": {"severity":"Minor","cause":"Viral infection or irritation.","symptoms":"Dry or productive cough.","prevention":"Avoid cold exposure, stay hydrated.","remedy":"Honey, warm fluids, cough syrup if needed."},
    "flu": {"severity":"Minor","cause":"Influenza virus infection.","symptoms":"Fever, fatigue, body ache, sore throat.","prevention":"Flu vaccine, hygiene, avoid sick contacts.","remedy":"Rest, fluids, paracetamol."},
    "stomach ache": {"severity":"Minor","cause":"Indigestion, gas, viral infection.","symptoms":"Abdominal pain, bloating.","prevention":"Eat properly, avoid junk food.","remedy":"Light meals, hydration, antacids if needed."},
    "diarrhea": {"severity":"Minor","cause":"Bacterial/viral infection, food poisoning.","symptoms":"Loose stools, dehydration.","prevention":"Clean water, hygiene.","remedy":"Hydration, ORS, consult doctor if severe."},
    "constipation": {"severity":"Minor","cause":"Low fiber diet, dehydration.","symptoms":"Difficulty passing stools, bloating.","prevention":"High-fiber diet, hydration, exercise.","remedy":"Fiber intake, hydration, mild laxatives."},
    "allergies": {"severity":"Minor","cause":"Immune reaction to allergens.","symptoms":"Sneezing, itching, rash.","prevention":"Avoid allergens, antihistamines if needed.","remedy":"Antihistamines, avoid triggers."},

    # Moderate Diseases
    "diabetes": {"severity":"Moderate","cause":"Body cannot produce or properly use insulin.","symptoms":"Frequent urination, excessive thirst, fatigue.","prevention":"Healthy diet, exercise, maintain weight.","remedy":"Medication, insulin, lifestyle changes."},
    "hypertension": {"severity":"Moderate","cause":"High blood pressure due to lifestyle/genetics.","symptoms":"Headache, dizziness, nosebleeds (sometimes asymptomatic).","prevention":"Low salt diet, exercise, avoid alcohol/smoking.","remedy":"Medication, lifestyle changes, monitor BP."},
    "asthma": {"severity":"Moderate","cause":"Inflammation of airways, triggers include allergens.","symptoms":"Shortness of breath, wheezing, coughing.","prevention":"Avoid triggers, regular checkups.","remedy":"Inhalers, medications, avoid allergens."},
    "migraine": {"severity":"Moderate","cause":"Neurological, triggered by stress, hormones, diet.","symptoms":"Severe headache, nausea, sensitivity to light/sound.","prevention":"Manage stress, avoid triggers, sleep well.","remedy":"Painkillers, rest, lifestyle management."},
    "gastritis": {"severity":"Moderate","cause":"Stomach lining inflammation due to infection or NSAIDs.","symptoms":"Stomach pain, nausea, indigestion.","prevention":"Avoid irritants, healthy diet.","remedy":"Antacids, medications, diet adjustments."},
    "uti": {"severity":"Moderate","cause":"Bacterial infection in urinary tract.","symptoms":"Painful urination, frequent urge to urinate.","prevention":"Hydration, hygiene, urinate after intercourse.","remedy":"Antibiotics, hydration."},
    "skin infection": {"severity":"Moderate","cause":"Bacterial or fungal infections.","symptoms":"Rash, redness, itching.","prevention":"Hygiene, avoid contaminated surfaces.","remedy":"Topical or oral medications."},
    "bronchitis": {"severity":"Moderate","cause":"Viral or bacterial infection of bronchi.","symptoms":"Cough, mucus, shortness of breath.","prevention":"Avoid smoking, good hygiene.","remedy":"Rest, fluids, medications if bacterial."},
    "anemia": {"severity":"Moderate","cause":"Low hemoglobin, nutritional deficiency or chronic disease.","symptoms":"Fatigue, weakness, pallor.","prevention":"Iron-rich diet, supplements if needed.","remedy":"Iron supplements, diet changes."},
    "thyroid disorder": {"severity":"Moderate","cause":"Hypo/Hyperthyroidism due to gland dysfunction.","symptoms":"Fatigue, weight changes, temperature sensitivity.","prevention":"Regular checkups, iodine-rich diet.","remedy":"Medication, monitoring hormone levels."},

    # Major Diseases
    "covid-19": {"severity":"Major","cause":"Infection by SARS-CoV-2 virus.","symptoms":"Fever, cough, shortness of breath, loss of taste/smell.","prevention":"Vaccination, masks, social distancing.","remedy":"Consult doctor, isolation, supportive care."},
    "heart disease": {"severity":"Major","cause":"Coronary artery disease, plaque buildup.","symptoms":"Chest pain, shortness of breath, fatigue.","prevention":"Healthy diet, exercise, avoid smoking.","remedy":"Medication, surgery, lifestyle changes."},
    "stroke": {"severity":"Major","cause":"Interruption of blood flow to brain.","symptoms":"Weakness, speech difficulty, facial droop.","prevention":"Control BP, healthy lifestyle.","remedy":"Immediate medical attention, rehabilitation."},
    "cancer": {"severity":"Major","cause":"Uncontrolled cell growth in body tissues.","symptoms":"Varies by type; lumps, fatigue, weight loss.","prevention":"Avoid carcinogens, healthy lifestyle, screenings.","remedy":"Surgery, chemotherapy, radiation therapy."},
    "ckd": {"severity":"Major","cause":"Chronic kidney damage over time.","symptoms":"Fatigue, swelling, decreased urine output.","prevention":"Control BP/diabetes, hydration.","remedy":"Dialysis, transplant, medications."},
    "liver disease": {"severity":"Major","cause":"Hepatitis, alcohol, fatty liver.","symptoms":"Jaundice, fatigue, nausea.","prevention":"Avoid alcohol, vaccination, healthy diet.","remedy":"Medications, lifestyle changes, transplant in severe cases."},
    "diabetes1": {"severity":"Major","cause":"Autoimmune destruction of insulin-producing cells.","symptoms":"High blood sugar, fatigue, frequent urination.","prevention":"No known prevention, early detection.","remedy":"Insulin therapy, monitoring blood sugar."},
    "tb": {"severity":"Major","cause":"Bacterial infection by Mycobacterium tuberculosis.","symptoms":"Cough, weight loss, fever, night sweats.","prevention":"Vaccination (BCG), avoid infected contact.","remedy":"Long-term antibiotics."},
    "pneumonia": {"severity":"Major","cause":"Lung infection (bacterial/viral).","symptoms":"Fever, cough, shortness of breath, chest pain.","prevention":"Vaccination, hygiene, avoid smoking.","remedy":"Antibiotics, hospitalization if severe."},
    "hiv": {"severity":"Major","cause":"Viral infection attacking the immune system.","symptoms":"Flu-like symptoms initially; long-term immune suppression.","prevention":"Safe sex, avoid sharing needles.","remedy":"Antiretroviral therapy (ART)."}
}

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feature" not in st.session_state:
    st.session_state.feature = "Doctor Help"
if "voice_lang" not in st.session_state:
    st.session_state.voice_lang = "en"

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Settings")
    new_feature = st.radio(
        "Features",
        ("Doctor Help", "Quantum Solver", "Assistant")
    )
    if new_feature != st.session_state.feature:
        st.session_state.feature = new_feature
        st.session_state.chat_history = []
    st.divider()
    st.subheader("🎙️ Voice Language")
    lang_options = {
        "🇺🇸 English": "en",
        "🇫🇷 French": "fr",
        "🇩🇪 German": "de",
        "🇮🇹 Italian": "it",
        "🇪🇸 Spanish": "es",
        "🇯🇵 Japanese": "ja",
        "🇰🇷 Korean": "ko",
        "🇨🇳 Chinese (Mandarin)": "zh-cn"
    }
    selected_lang = st.selectbox("Select Language", list(lang_options.keys()))
    st.session_state.voice_lang = lang_options[selected_lang]
    st.divider()
    st.header("📜 Chat History")
    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

# ---------- PAGE TITLE ----------
page_titles = {
    "Doctor Help": "🤖 AI Doctor",
    "Quantum Solver": "🤖 Quantum Professor",
    "Assistant": "🤖 AI Assistant"
}
st.set_page_config(page_title=page_titles.get(st.session_state.feature, "🤖 AI Assistant"), layout="wide")
st.title(page_titles.get(st.session_state.feature, "🤖 AI Assistant"))

# ---------- CHAT INPUT ----------
user_input = st.text_input("Type your message here...").lower()

if user_input:
    bot_response = ""
    st.session_state.chat_history.append(("You", user_input))

    if st.session_state.feature == "Doctor Help":
        # Symptom-based suggestion
        found_diseases = []
        for disease, info in disease_data.items():
            if disease in user_input or any(symptom.lower() in user_input for symptom in info['symptoms'].split(", ")):
                found_diseases.append(f"**{disease.title()} ({info['severity']})**: {info['remedy']}")
        if found_diseases:
            bot_response = "Possible diseases based on your input:\n" + "\n".join(found_diseases)
        else:
            bot_response = "I am here to help with health-related questions."

    elif st.session_state.feature == "Quantum Solver":
        try:
            expr = parse_expr(user_input)
            simplified = simplify(expr)
            bot_response = f"✅ Simplified Result: {simplified}"
        except:
            bot_response = "I couldn't parse the math problem."

    elif st.session_state.feature == "Assistant":
        try:
            summary = wikipedia.summary(user_input, sentences=2)
            bot_response = summary
        except:
            bot_response = "Sorry, I couldn't find information on that topic."

    st.session_state.chat_history.append(("Bot", bot_response))
    speak_text(bot_response, lang=st.session_state.voice_lang)

# ---------- DISPLAY CHAT ----------
for speaker, text in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**🧑 You:** {text}")
    else:
        st.markdown(f"**🤖 Bot:** {text}")
