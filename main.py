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

# ---------- QUANTUM & MATH FUNCTIONS ----------
def solve_equation(eq_str, var_str):
    var = sp.symbols(var_str)
    eq = parse_expr(eq_str)
    solution = sp.solve(eq, var)
    return f"Solve {eq} for {var} → Solution: {solution}"

def differentiate(expr_str, var_str):
    var = sp.symbols(var_str)
    expr = parse_expr(expr_str)
    derivative = sp.diff(expr, var)
    return f"Differentiating {expr} w.r.t {var} → Result: {derivative}"

def integrate_expr(expr_str, var_str):
    var = sp.symbols(var_str)
    expr = parse_expr(expr_str)
    integral = sp.integrate(expr, var)
    return f"Integrating {expr} w.r.t {var} → Result: {integral}"

def dagger_expr(expr_str):
    expr = parse_expr(expr_str)
    dag = Dagger(expr)
    return f"Hermitian conjugate (dagger) of {expr} → {dag}"

def quantum_eigen(matrix_list):
    try:
        mat = sp.Matrix(matrix_list)
        eigenvals = mat.eigenvals()
        eigenvects = mat.eigenvects()
        return f"Eigenvalues: {eigenvals}\nEigenvectors: {eigenvects}"
    except Exception as e:
        return f"Error: {e}"

def expectation_value(matrix_list, state_list):
    try:
        mat = sp.Matrix(matrix_list)
        state = sp.Matrix(state_list)
        val = (state.T * mat * state)[0]
        return f"Expectation value: {val}"
    except Exception as e:
        return f"Error: {e}"

def explain_quantum_concept(concept):
    concept = concept.lower()
    theory = {
        "wavefunction": ("A wavefunction Ψ represents a quantum state; |Ψ|^2 is probability density.", 
                         "https://en.wikipedia.org/wiki/Wave_function"),
        "operator": ("Operator acts on a wavefunction to extract physical info.", 
                     "https://en.wikipedia.org/wiki/Quantum_operator"),
        "eigenvalue": ("Eigenvalue λ satisfies ÔΨ = λΨ, representing measurable quantities.", 
                       "https://en.wikipedia.org/wiki/Eigenvalues_and_eigenvectors"),
        "schrodinger equation": ("HΨ = iħ ∂Ψ/∂t governs time evolution of quantum states.", 
                                 "https://en.wikipedia.org/wiki/Schr%C3%B6dinger_equation"),
        "commutator": ("[A,B]=AB-BA; non-zero commutator → observables cannot be simultaneously measured.", 
                       "https://en.wikipedia.org/wiki/Commutator"),
        "expectation value": ("Expectation value <Ψ|O|Ψ> gives average measured value of observable.", 
                              "https://en.wikipedia.org/wiki/Expectation_value_(quantum_mechanics)")
    }
    if concept in theory:
        desc, link = theory[concept]
        return f"{desc} More info: [Link]({link})"
    else:
        return "Sorry, concept not found. Check [Quantum Mechanics Wikipedia](https://en.wikipedia.org/wiki/Quantum_mechanics)."

# ---------- DISEASE DATABASE ----------
disease_data = {
    "cold": { "cause": "Viral infection of the upper respiratory tract.", "symptoms": "Sneezing, runny nose, mild fever, sore throat.", "prevention": "Wash hands, avoid cold exposure, stay warm.", "remedy": "Steam inhalation, rest, warm fluids."},
    "headache": {"cause": "Stress, dehydration, migraine.", "symptoms": "Pain in head, sensitivity to light, nausea.", "prevention": "Hydration, sleep well, reduce stress.", "remedy": "Hydration, rest, mild painkillers."},
    "fever": {"cause": "Often viral or bacterial infections.", "symptoms": "High body temperature, chills, body ache.", "prevention": "Maintain hygiene, stay hydrated.", "remedy": "Paracetamol, rest, consult doctor if persistent."},
    "sore throat": { "cause": "Viral or bacterial infection.", "symptoms": "Painful throat, difficulty swallowing.", "prevention": "Avoid cold drinks, wash hands.", "remedy": "Warm salt water gargle, rest."},
    "cough": {"cause": "Viral infection or irritation.", "symptoms": "Dry or productive cough.", "prevention": "Avoid cold exposure, stay hydrated.", "remedy": "Honey, warm fluids, cough syrup if needed."},
    "flu": { "cause": "Influenza virus infection.", "symptoms": "Fever, fatigue, body ache, sore throat.", "prevention": "Flu vaccine, hygiene, avoid sick contacts.", "remedy": "Rest, fluids, paracetamol."},
    "stomach ache": { "cause": "Indigestion, gas, viral infection.", "symptoms": "Abdominal pain, bloating.", "prevention": "Eat properly, avoid junk food.", "remedy": "Light meals, hydration, antacids if needed."},
    "diarrhea": {"cause": "Bacterial/viral infection, food poisoning.", "symptoms": "Loose stools, dehydration.", "prevention": "Clean water, hygiene.", "remedy": "Hydration, ORS, consult doctor if severe."},
    "constipation": {"cause": "Low fiber diet, dehydration.", "symptoms": "Difficulty passing stools, bloating.", "prevention": "High-fiber diet, hydration, exercise.", "remedy": "Fiber intake, hydration, mild laxatives."},
    "allergies": { "cause": "Immune reaction to allergens.", "symptoms": "Sneezing, itching, rash.", "prevention": "Avoid allergens, antihistamines if needed.", "remedy": "Antihistamines, avoid triggers."},
    "diabetes": { "cause": "Body cannot produce or properly use insulin.", "symptoms": "Frequent urination, excessive thirst, fatigue.", "prevention": "Healthy diet, exercise, maintain weight.", "remedy": "Medication, insulin, lifestyle changes."},
    "hypertension": {"cause": "High blood pressure due to lifestyle/genetics.", "symptoms": "Headache, dizziness, nosebleeds (sometimes asymptomatic).", "prevention": "Low salt diet, exercise, avoid alcohol/smoking.", "remedy": "Medication, lifestyle changes, monitor BP."},
    "asthma": { "cause": "Inflammation of airways, triggers include allergens.", "symptoms": "Shortness of breath, wheezing, coughing.", "prevention": "Avoid triggers, regular checkups.", "remedy": "Inhalers, medications, avoid allergens."},
    "migraine": { "cause": "Neurological, triggered by stress, hormones, diet.", "symptoms": "Severe headache, nausea, sensitivity to light/sound.", "prevention": "Manage stress, avoid triggers, sleep well.", "remedy": "Painkillers, rest, lifestyle management."},
    "gastritis": { "cause": "Stomach lining inflammation due to infection or NSAIDs.", "symptoms": "Stomach pain, nausea, indigestion.", "prevention": "Avoid irritants, healthy diet.", "remedy": "Antacids, medications, diet adjustments."},
    "uti": { "cause": "Bacterial infection in urinary tract.", "symptoms": "Painful urination, frequent urge to urinate.", "prevention": "Hydration, hygiene, urinate after intercourse.", "remedy": "Antibiotics, hydration."},
    "skin infection": {"cause": "Bacterial or fungal infections.", "symptoms": "Rash, redness, itching.", "prevention": "Hygiene, avoid contaminated surfaces.", "remedy": "Topical or oral medications."},
    "bronchitis": { "cause": "Viral or bacterial infection of bronchi.", "symptoms": "Cough, mucus, shortness of breath.", "prevention": "Avoid smoking, good hygiene.", "remedy": "Rest, fluids, medications if bacterial."},
    "anemia": { "cause": "Low hemoglobin, nutritional deficiency or chronic disease.", "symptoms": "Fatigue, weakness, pallor.", "prevention": "Iron-rich diet, supplements if needed.", "remedy": "Iron supplements, diet changes."},
    "thyroid disorder": { "cause": "Hypo/Hyperthyroidism due to gland dysfunction.", "symptoms": "Fatigue, weight changes, temperature sensitivity.", "prevention": "Regular checkups, iodine-rich diet.", "remedy": "Medication, monitoring hormone levels."},
    "covid-19": { "cause": "Infection by SARS-CoV-2 virus.", "symptoms": "Fever, cough, shortness of breath, loss of taste/smell.", "prevention": "Vaccination, masks, social distancing.", "remedy": "Consult doctor, isolation, supportive care."},
    "heart disease": { "cause": "Coronary artery disease, plaque buildup.", "symptoms": "Chest pain, shortness of breath, fatigue.", "prevention": "Healthy diet, exercise, avoid smoking.", "remedy": "Medication, surgery, lifestyle changes."},
    "stroke": { "cause": "Interruption of blood flow to brain.", "symptoms": "Weakness, speech difficulty, facial droop.", "prevention": "Control BP, healthy lifestyle.", "remedy": "Immediate medical attention, rehabilitation."},
    "cancer": { "cause": "Uncontrolled cell growth in body tissues.", "symptoms": "Varies by type; lumps, fatigue, weight loss.", "prevention": "Avoid carcinogens, healthy lifestyle, screenings.", "remedy": "Surgery, chemotherapy, radiation therapy."},
    "ckd": { "cause": "Chronic kidney damage over time.", "symptoms": "Fatigue, swelling, decreased urine output.", "prevention": "Control BP/diabetes, hydration.", "remedy": "Dialysis, transplant, medications."},
    "liver disease": {"cause": "Hepatitis, alcohol, fatty liver.", "symptoms": "Jaundice, fatigue, nausea.", "prevention": "Avoid alcohol, vaccination, healthy diet.", "remedy": "Medications, lifestyle changes, transplant in severe cases."},
    "tb": { "cause": "Bacterial infection by Mycobacterium tuberculosis.", "symptoms": "Cough, weight loss, fever, night sweats.", "prevention": "Vaccination (BCG), avoid infected contact.", "remedy": "Long-term antibiotics."},
    "pneumonia": { "cause": "Lung infection (bacterial/viral).", "symptoms": "Fever, cough, shortness of breath, chest pain.", "prevention": "Vaccination, hygiene, avoid smoking.", "remedy": "Antibiotics, hospitalization if severe."},
    "hiv": { "cause": "Viral infection attacking the immune system.", "symptoms": "Flu-like symptoms initially; long-term immune suppression.", "prevention": "Safe sex, avoid sharing needles.", "remedy": "Antiretroviral therapy (ART)."}
}

# ---------- SESSION STATE ----------
for key in ["chat_history", "feature", "last_image", "last_link", "last_bot_response", "current_display_history", "voice_lang"]:
    if key not in st.session_state:
        st.session_state[key] = "" if "bot_response" in key else []

if "feature" not in st.session_state:
    st.session_state.feature = "Doctor Help"
if "voice_lang" not in st.session_state:
    st.session_state.voice_lang = "en"

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Settings")
    new_feature = st.radio("Features", ("Doctor Help", "Quantum Solver", "Assistant"))
    if new_feature != st.session_state.feature:
        st.session_state.feature = new_feature
        st.session_state.current_display_history = []
        st.session_state.last_bot_response = ""
        st.session_state.last_image = None
        st.session_state.last_link = None
    st.divider()
    st.subheader("🎙️ Voice Language")
    lang_options = { "Afrikaans":"af","Albanian":"sq","Amharic":"am","Arabic":"ar","Armenian":"hy","Azerbaijani":"az",
        "Basque":"eu","Belarusian":"be","Bengali":"bn","Bosnian":"bs","Bulgarian":"bg","Catalan":"ca",
        "Cebuano":"ceb","Chichewa":"ny","Chinese (Simplified)":"zh-cn","Chinese (Traditional)":"zh-tw",
        "Corsican":"co","Croatian":"hr","Czech":"cs","Danish":"da","Dutch":"nl","English":"en",
        "Esperanto":"eo","Estonian":"et","Filipino":"tl","Finnish":"fi","French":"fr","Frisian":"fy",
        "Galician":"gl","Georgian":"ka","German":"de","Greek":"el","Gujarati":"gu","Haitian Creole":"ht",
        "Hausa":"ha","Hawaiian":"haw","Hebrew":"he","Hindi":"hi","Hmong":"hmn","Hungarian":"hu",
        "Icelandic":"is","Igbo":"ig","Indonesian":"id","Irish":"ga","Italian":"it","Japanese":"ja",
        "Javanese":"jv","Kannada":"kn","Kazakh":"kk","Khmer":"km","Kinyarwanda":"rw","Korean":"ko",
        "Kurdish (Kurmanji)":"ku","Kyrgyz":"ky","Lao":"lo","Latin":"la","Latvian":"lv","Lithuanian":"lt",
        "Luxembourgish":"lb","Macedonian":"mk","Malagasy":"mg","Malay":"ms","Malayalam":"ml","Maltese":"mt",
        "Maori":"mi","Marathi":"mr","Mongolian":"mn","Myanmar (Burmese)":"my","Nepali":"ne","Norwegian":"no",
        "Odia (Oriya)":"or","Pashto":"ps","Persian":"fa","Polish":"pl","Portuguese":"pt","Punjabi":"pa",
        "Romanian":"ro","Russian":"ru","Samoan":"sm","Scots Gaelic":"gd","Serbian":"sr","Sesotho":"st",
        "Shona":"sn","Sindhi":"sd","Sinhala":"si","Slovak":"sk","Slovenian":"sl","Somali":"so",
        "Spanish":"es","Sundanese":"su","Swahili":"sw","Swedish":"sv","Tajik":"tg","Tamil":"ta",
        "Tatar":"tt","Telugu":"te","Thai":"th","Turkish":"tr","Turkmen":"tk","Ukrainian":"uk",
        "Urdu":"ur","Uyghur":"ug","Uzbek":"uz","Vietnamese":"vi","Welsh":"cy","Xhosa":"xh",
        "Yiddish":"yi","Yoruba":"yo","Zulu":"zu"}
    selected_lang = st.selectbox("Select Language", list(lang_options.keys()))
    st.session_state.voice_lang = lang_options[selected_lang]
    st.divider()
    st.header("📜 Chat History")
    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

# ---------- PAGE TITLE ----------
page_titles = {"Doctor Help":"🤖 AI Doctor","Quantum Solver":"🤖 Quantum Professor","Assistant":"🤖 AI Assistant"}
current_title = page_titles.get(st.session_state.feature,"🤖 AI Assistant")
st.set_page_config(page_title=current_title, page_icon="🤖", layout="wide")
st.title(current_title)

# ---------- DISPLAY CHAT ----------
for sender, msg in st.session_state.current_display_history:
    st.markdown(f"**🧑 You:** {msg}" if sender=="You" else f"**🤖 Bot:** {msg}")

# ---------- CHAT INPUT ----------
user_input = st.text_input("Type your message here...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.current_display_history.append(("You", user_input))
    user_input_lower = user_input.lower()
    bot_response = ""

    # ---------- DOCTOR FEATURE ----------
    if st.session_state.feature == "Doctor Help":
        found = False
        for disease, info in disease_data.items():
            if disease in user_input_lower:
                bot_response = f"**Disease:** {disease.title()} Cause: {info['cause']}\n• Symptoms: {info['symptoms']}\n• Prevention: {info['prevention']}\n• Remedy: {info['remedy']}"
                found = True
                break
        if not found:
            if user_input_lower.strip() in ["hi","hello"]:
                bot_response = "Hello! I am your personal AI doctor. How can I help you?"
            else:
                bot_response = "I am here to help with health-related questions."

    # ---------- QUANTUM FEATURE ----------
    elif st.session_state.feature == "Quantum Solver":
        input_lower = user_input_lower
        if input_lower.strip() in ["hi","hello"]:
            bot_response = "Hi! I am your Quantum Professor. How can I help you today?"
        elif "solve" in input_lower:
            try:
                parts = input_lower.split("for")
                eq_str = parts[0].replace("solve","").strip()
                var_str = parts[1].strip()
                bot_response = solve_equation(eq_str,var_str)
            except:
                bot_response = "Use format: 'Solve <equation> for <variable>'."
        elif "differentiate" in input_lower:
            try:
                parts = input_lower.split("for")
                expr_str = parts[0].replace("differentiate","").strip()
                var_str = parts[1].strip()
                bot_response = differentiate(expr_str,var_str)
            except:
                bot_response = "Use format: 'Differentiate <expression> for <variable>'."
        elif "integrate" in input_lower:
            try:
                parts = input_lower.split("for")
                expr_str = parts[0].replace("integrate","").strip()
                var_str = parts[1].strip()
                bot_response = integrate_expr(expr_str,var_str)
            except:
                bot_response = "Use format: 'Integrate <expression> for <variable>'."
        elif "dagger" in input_lower:
            expr_str = input_lower.replace("dagger","").strip()
            bot_response = dagger_expr(expr_str)
        elif "eigen" in input_lower:
            try:
                matrix_str = user_input.split("[",1)[1].rsplit("]",1)[0]
                matrix_list = eval("["+matrix_str+"]")
                bot_response = quantum_eigen(matrix_list)
            except:
                bot_response = "Use format: 'Eigen [[a,b],[c,d]]'"
        elif "expectation" in input_lower:
            try:
                parts = user_input.split("] [")
                matrix_list = eval(parts[0].split("[",1)[1]+"]")
                state_list = eval("["+parts[1].replace("]","")+"]")
                bot_response = expectation_value(matrix_list,state_list)
            except:
                bot_response = "Use format: 'Expectation [[O]] [state]'"
        else:
            try:
                expr = parse_expr(user_input_lower)
                simplified = simplify(expr)
                bot_response = f"Simplified Result: {simplified}"
            except:
                try:
                    if "=" in user_input:
                        lhs,rhs = user_input.split("=")
                        x = symbols('x')
                        eq = Eq(parse_expr(lhs),parse_expr(rhs))
                        sol = solve(eq,x)
                        bot_response = f"Solution: {sol}"
                    else:
                        bot_response = "Invalid math expression."
                except:
                    bot_response = "I couldn't parse the math problem."

    # ---------- ASSISTANT FEATURE (FRIENDLY + WIKI LINK) ----------
    elif st.session_state.feature == "Assistant":
        user_query = user_input.strip()
        user_query_lower = user_query.lower()

        greetings = ["hi","hello","hey"]
        if user_query_lower in greetings:
            bot_response = "Hello! How's it going?"
            st.session_state.last_image = None
            st.session_state.last_link = None
        else:
            try:
                summary = wikipedia.summary(user_query, sentences=2, auto_suggest=True, redirect=True)
                page = wikipedia.page(user_query, auto_suggest=True, redirect=True)
                bot_response = f"{summary} More info: [Link]({page.url})"
                st.session_state.last_image = page.images[0] if page.images else None
                st.session_state.last_link = page.url
            except wikipedia.DisambiguationError as e:
                first_option = e.options[0]
                try:
                    summary = wikipedia.summary(first_option, sentences=2)
                    page = wikipedia.page(first_option)
                    bot_response = f"{summary} More info: [Link]({page.url})"
                    st.session_state.last_image = page.images[0] if page.images else None
                    st.session_state.last_link = page.url
                except:
                    bot_response = f"This topic is ambiguous. Did you mean: {', '.join(e.options[:5])}?"
                    st.session_state.last_image = None
                    st.session_state.last_link = None
            except wikipedia.PageError:
                bot_response = "Sorry, I couldn't find information on that topic."
                st.session_state.last_image = None
                st.session_state.last_link = None

    # ---------- SAVE RESPONSE & SPEAK ----------
    st.session_state.chat_history.append(("Bot",bot_response))
    st.session_state.current_display_history.append(("Bot",bot_response))
    st.session_state.last_bot_response = bot_response
    speak_text(bot_response, lang=st.session_state.voice_lang)

# ---------- SHOW BOT RESPONSE ----------
if st.session_state.last_bot_response:
    st.markdown(f"**🤖 Bot:** {st.session_state.last_bot_response}")

# ---------- DISPLAY ASSISTANT IMAGE/LINK ----------
if st.session_state.feature=="Assistant":
    if st.session_state.last_image:
        st.image(st.session_state.last_image,width=200)
    if st.session_state.last_link:
        st.markdown(f"[More Info 🔗]({st.session_state.last_link})")

# ---------- SMALL LIT HEART ----------
st.markdown("""
<style>
.lit-heart {position: fixed;bottom: 5px;left: 50%;transform: translateX(-50%);font-size: 20px;color: red;animation: pulse 1s infinite;}
@keyframes pulse {0% {transform: translateX(-50%) scale(1);}50% {transform: translateX(-50%) scale(1.2);}100% {transform: translateX(-50%) scale(1);}
</style>
<div class="lit-heart">❤️</div>
""", unsafe_allow_html=True)

