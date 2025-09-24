import streamlit as st
from gtts import gTTS
import base64
import wikipedia
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.physics.quantum import Dagger

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

# ---------- QUANTUM SOLVER FUNCTIONS ----------
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

# ---------- SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feature" not in st.session_state:
    st.session_state.feature = "Doctor Help"
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_link" not in st.session_state:
    st.session_state.last_link = None
if "last_bot_response" not in st.session_state:
    st.session_state.last_bot_response = ""
if "current_display_history" not in st.session_state:
    st.session_state.current_display_history = []
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
        st.session_state.current_display_history = []
        st.session_state.last_bot_response = ""
        st.session_state.last_image = None
        st.session_state.last_link = None
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

# ---------- DYNAMIC PAGE TITLE ----------
page_titles = {
    "Doctor Help": "🤖 AI Doctor",
    "Quantum Solver": "🤖 Quantum Professor",
    "Assistant": "🤖 AI Assistant"
}
current_title = page_titles.get(st.session_state.feature, "🤖 AI Assistant")
st.set_page_config(page_title=current_title, page_icon="🤖", layout="wide")
st.title(current_title)

# ---------- DISPLAY CURRENT CHAT ----------
for sender, msg in st.session_state.current_display_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

# ---------- CHAT INPUT ----------
user_input = st.text_input("Type your message here...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.current_display_history.append(("You", user_input))
    user_input_lower = user_input.lower()
    bot_response = ""

    # ---------- FEATURE LOGIC ----------
    if st.session_state.feature == "Doctor Help":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hello! I am your personal AI doctor. How can I help you?"
        elif "fever" in user_input_lower:
            bot_response = (
                "🤒 Fever\n• Cause: Usually infections.\n• Prevention: Hydrate & rest.\n• Remedy: Paracetamol if needed."
            )
        elif "cold" in user_input_lower:
            bot_response = (
                "🤧 Cold\n• Cause: Viral infection.\n• Prevention: Wash hands.\n• Remedy: Steam inhalation & rest."
            )
        elif "headache" in user_input_lower:
            bot_response = (
                "🤕 Headache\n• Cause: Stress, dehydration.\n• Prevention: Hydrate & rest.\n• Remedy: Mild painkillers."
            )
        else:
            bot_response = "I am here to help with health-related questions."

    elif st.session_state.feature == "Quantum Solver":
        input_lower = user_input.lower()
        if "hi" in input_lower or "hello" in input_lower:
            bot_response = "Hi! I am your Quantum Professor. Ask me a math problem or quantum concept."
        elif "solve" in input_lower:
            try:
                parts = input_lower.split("for")
                eq_str = parts[0].replace("solve", "").strip()
                var_str = parts[1].strip()
                bot_response = solve_equation(eq_str, var_str)
            except:
                bot_response = "Use format: 'Solve <equation> for <variable>'."
        elif "differentiate" in input_lower:
            try:
                parts = input_lower.split("for")
                expr_str = parts[0].replace("differentiate", "").strip()
                var_str = parts[1].strip()
                bot_response = differentiate(expr_str, var_str)
            except:
                bot_response = "Use format: 'Differentiate <expression> for <variable>'."
        elif "integrate" in input_lower:
            try:
                parts = input_lower.split("for")
                expr_str = parts[0].replace("integrate", "").strip()
                var_str = parts[1].strip()
                bot_response = integrate_expr(expr_str, var_str)
            except:
                bot_response = "Use format: 'Integrate <expression> for <variable>'."
        elif "dagger" in input_lower:
            expr_str = input_lower.replace("dagger", "").strip()
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
                bot_response = expectation_value(matrix_list, state_list)
            except:
                bot_response = "Use format: 'Expectation [[O]] [state]'"
        else:
            bot_response = explain_quantum_concept(user_input)

    elif st.session_state.feature == "Assistant":
        if "hi" in user_input_lower or "hello" in user_input_lower:
            bot_response = "Hello! Ask me about any topic and I will fetch info from Wikipedia."
            st.session_state.last_image = None
            st.session_state.last_link = None
        else:
            try:
                summary = wikipedia.summary(user_input, sentences=2)
                page = wikipedia.page(user_input)
                bot_response = summary
                st.session_state.last_image = page.images[0] if page.images else None
                st.session_state.last_link = page.url
            except:
                bot_response = "Sorry, I couldn't find information on that topic."
                st.session_state.last_image = None
                st.session_state.last_link = None

    # Save response and speak
    st.session_state.chat_history.append(("Bot", bot_response))
    st.session_state.current_display_history.append(("Bot", bot_response))
    st.session_state.last_bot_response = bot_response
    speak_text(bot_response, lang=st.session_state.voice_lang)

# ---------- SHOW BOT RESPONSE BELOW INPUT ----------
if st.session_state.last_bot_response:
    st.markdown(f"**🤖 Bot:** {st.session_state.last_bot_response}")

# ---------- DISPLAY ASSISTANT IMAGE/LINK ----------
if st.session_state.feature == "Assistant":
    if st.session_state.last_image:
        st.image(st.session_state.last_image, width=200)
    if st.session_state.last_link:
        st.markdown(f"[More Info 🔗]({st.session_state.last_link})")

# ---------- SMALL LIT HEART AT BOTTOM ----------
st.markdown(
    """
    <style>
    .lit-heart {
        position: fixed;
        bottom: 5px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 20px;
        color: red;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: translateX(-50%) scale(1); }
        50% { transform: translateX(-50%) scale(1.2); }
        100% { transform: translateX(-50%) scale(1); }
    }
    </style>
    <div class="lit-heart">❤️</div>
    """,
    unsafe_allow_html=True
)
