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
    "diabetes": { "cause": "Body cannot produce or properly use insulin.", "symptoms": "Frequent urination, excessive thirst, fatigue.", "prevention": "Healthy diet, exercise, maintain weight.", "remedy": "Medication, insulin, lifestyle changes."}
    # Add remaining diseases as needed
}

# ---------- SESSION STATE ----------
for key in ["chat_history", "feature", "last_image", "last_link", "last_bot_response", "current_display_history", "voice_lang"]:
    if key not in st.session_state:
        st.session_state[key] = "" if "bot_response" in key else []

if "feature" not in st.session_state:
    st.session_state.feature = "Assistant"
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
    lang_options = {"🇺🇸 English":"en","🇫🇷 French":"fr","🇩🇪 German":"de","🇮🇹 Italian":"it","🇪🇸 Spanish":"es","🇯🇵 Japanese":"ja","🇰🇷 Korean":"ko","🇨🇳 Chinese (Mandarin)":"zh-cn"}
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

    # ---------- ASSISTANT FEATURE ----------
    if st.session_state.feature == "Assistant":
        user_query = user_input.strip()
        user_query_lower = user_query.lower()

        # Greetings
        if any(greet in user_query_lower for greet in ["hi","hello","hey"]):
            bot_response = "Hello! How's it going?"
            st.session_state.last_image = None
            st.session_state.last_link = None
        else:
            # Wikipedia search
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
