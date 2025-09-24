import streamlit as st
from gtts import gTTS
import base64
import wikipedia
from sympy import symbols, Eq, solve, simplify, factor, diff, integrate, Poly
from sympy.parsing.sympy_parser import parse_expr
import re

# ---------- APP CONFIG (single call) ----------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# ---------- UTILS: TEXT-TO-SPEECH AUTOPLAY ----------
def speak_text_autoplay(text: str):
    """Create an autoplaying audio element from text using gTTS (English)."""
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tfile = "voice.mp3"
        tts.save(tfile)
        with open(tfile, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""<audio autoplay>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>"""
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        # Fail silently for TTS problems
        pass

# ---------- HELPERS FOR QUANTUM SOLVER ----------
def _safe_parse(expr_str: str):
    """Replace ^ with ** and parse with sympy (best-effort)."""
    expr_str = expr_str.replace("^", "**")
    # remove commas that might break parse in some user inputs
    try:
        return parse_expr(expr_str, evaluate=True)
    except Exception:
        # fallback: try replacing unicode minus etc.
        expr_str = expr_str.replace("−", "-")
        return parse_expr(expr_str, evaluate=False)

def quantum_details_for_expression(user_text: str, show_steps: bool):
    """Return a string describing simplification, factorization, numeric evaluation, optionally steps."""
    txt = user_text.strip()
    expr = _safe_parse(txt)
    simplified = simplify(expr)
    factored = factor(expr)
    # numeric evaluation if purely numeric
    numeric = None
    try:
        numeric = float(expr.evalf())
    except Exception:
        numeric = None

    result = f"🔬 **Quantum Simplification**\n\nExpression: `{txt}`\n\n"
    result += f"**Simplified:** `{simplified}`\n\n"
    if factored != simplified:
        result += f"**Factored:** `{factored}`\n\n"
    if numeric is not None:
        result += f"**Numeric (eval):** `{numeric}`\n\n"
    if show_steps:
        # simple "steps" explanation
        result += "**Steps (conceptual):**\n"
        result += "1. Parsed expression into symbolic form.\n"
        result += "2. Applied algebraic simplification rules (combine like terms, reduce fractions).\n"
        if factored != simplified:
            result += "3. Factored the polynomial/expression where applicable.\n"
        result += "4. Evaluated numerically if numbers present.\n\n"
        result += "Note: For advanced step-by-step algebraic transformations, specify a clearer request (e.g., 'solve x^2-2x+1=0 steps').\n"
    return result

def quantum_solve_equation(user_text: str, show_steps: bool):
    """Solve equations with steps for linear/quadratic if requested."""
    lhs, rhs = user_text.split("=", 1)
    lhs_e = _safe_parse(lhs)
    rhs_e = _safe_parse(rhs)
    eq = Eq(lhs_e, rhs_e)
    free_vars = list(eq.free_symbols)
    if not free_vars:
        # no variable - test equality
        val = simplify(lhs_e - rhs_e)
        return f"Equation simplifies to `{val}` (0 means equality holds).", None
    var = free_vars[0]
    sols = solve(eq, var)
    result = f"🔬 **Quantum Equation Solve**\n\nEquation: `{lhs.strip()} = {rhs.strip()}`\n\n"
    result += f"**Solution(s) for {var}:** `{sols}`\n\n"
    # steps for degree 1 or 2 polynomials
    try:
        poly = Poly(lhs_e - rhs_e, var)
        deg = poly.degree()
    except Exception:
        poly = None
        deg = None

    if show_steps and deg is not None:
        if deg == 1:
            a = poly.coeffs()[0] if poly.coeffs() else None
            # linear steps (generic)
            result += "**Steps (linear):**\n1. Rearranged to standard form `ax + b = 0`.\n"
            result += "2. Isolated x: `x = -b/a`.\n\n"
        elif deg == 2:
            coeffs = poly.all_coeffs()  # [a, b, c]
            if len(coeffs) >= 3:
                a, b, c = coeffs[0], coeffs[1], coeffs[2]
                disc = b**2 - 4*a*c
                result += "**Steps (quadratic):**\n"
                result += f"1. Identify coefficients: a={a}, b={b}, c={c}\n"
                result += f"2. Compute discriminant: Δ = b² - 4ac = `{disc}`\n"
                result += "3. Roots: x = (-b ± sqrt(Δ)) / (2a)\n\n"
    # add small quantum analogy
    result += "📘 (Analogy) In quantum terms, solving finds the eigenstates where the variable collapses to classical values.\n"
    return result, sols

def quantum_calculus(user_text: str, show_steps: bool):
    """Handle `integrate` and `diff` requests in a simple way."""
    low = user_text.lower()
    if "integrate" in low:
        # attempt to extract expression after 'integrate'
        expr_str = re.sub(r"integrate\s*", "", low, flags=re.IGNORECASE).strip(" ()")
        if not expr_str:
            return "Specify what to integrate, e.g. `integrate x**2`."
        expr = _safe_parse(expr_str)
        x = list(expr.free_symbols)
        var = x[0] if x else symbols('x')
        res = integrate(expr, var)
        text = f"∫ {expr_str} d{var} = `{res}`\n"
        if show_steps:
            text += "Steps: symbolically applied integration rules (power rule, linearity)."
        return text
    if "diff" in low or "deriv" in low or "differentiate" in low:
        expr_str = re.sub(r"(diff|differentiate|derivative of)\s*", "", low, flags=re.IGNORECASE).strip(" ()")
        if not expr_str:
            return "Specify what to differentiate, e.g. `diff x**2`."
        expr = _safe_parse(expr_str)
        x = list(expr.free_symbols)
        var = x[0] if x else symbols('x')
        res = diff(expr, var)
        text = f"d/d{var} ({expr_str}) = `{res}`\n"
        if show_steps:
            text += "Steps: used power rule and linearity of differentiation."
        return text
    return None

# ---------- SESSION STATE INIT ----------
FEATURES = ["Doctor Help", "Quantum Professor", "Assistant"]  # show labels; will map to internal keys
if "current_feature" not in st.session_state:
    st.session_state.current_feature = "Doctor Help"
if "history_all" not in st.session_state:
    # global history for sidebar preview (list of (feature, sender, msg))
    st.session_state.history_all = []
if "current_chat" not in st.session_state:
    # per-feature main chat (cleared on switching)
    st.session_state.current_chat = {f: [] for f in FEATURES}
if "last_processed" not in st.session_state:
    st.session_state.last_processed = None
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_link" not in st.session_state:
    st.session_state.last_link = None

# ---------- SIDEBAR (left) ----------
st.sidebar.title("🤖 Features & History")

# Feature selector (unique key)
selected = st.sidebar.radio("Choose Feature:", ("Doctor Help", "Quantum Professor", "Assistant"), key="feature_radio_v2")

# When switching features: clear the main display for that feature
if selected != st.session_state.current_feature:
    st.session_state.current_feature = selected
    st.session_state.current_chat[selected] = []  # reset main conversation for the newly selected feature
    st.session_state.last_image = None
    st.session_state.last_link = None
    st.session_state.last_processed = None  # avoid accidental reprocessing

st.sidebar.markdown("---")
st.sidebar.subheader("📜 Global Chat History (preview)")
# show last few entries from history_all
if st.session_state.history_all:
    for feat, sender, msg in st.session_state.history_all[-12:]:
        short = msg if len(msg) <= 80 else msg[:77] + "..."
        st.sidebar.markdown(f"**{feat} / {sender}:** {short}")
else:
    st.sidebar.info("No chats yet. Type something to begin.")

st.sidebar.markdown("---")
# Optional manual clear for the active feature's main chat
if st.sidebar.button("Clear current conversation", key="clear_current"):
    st.session_state.current_chat[st.session_state.current_feature] = []

# ---------- MAIN AREA TITLE (dynamic) ----------
title_map = {
    "Doctor Help": "🤖 AI Doctor",
    "Quantum Professor": "🤖 AI Professor",
    "Assistant": "🤖 AI Assistant"
}
st.header(title_map.get(st.session_state.current_feature, "🤖 AI Assistant"))

# ---------- INPUT (top of main column) ----------
# single input widget with unique key
user_input = st.text_input("Type your message and press Enter", key="main_input")

# Process input only once (when it changes)
if user_input and st.session_state.last_processed != user_input:
    feat = st.session_state.current_feature
    low = user_input.strip()
    low_lower = low.lower()
    bot_reply = None

    # ---------- DOCTOR ----------
    if feat == "Doctor Help":
        if low_lower in ("hi", "hello", "hey"):
            bot_reply = "Hello! I am your personal AI doctor. How can I help you?"
        elif "fever" in low_lower:
            bot_reply = (
                "🤒 **Fever**\n\n"
                "**Causes:** Viral or bacterial infections (flu, cold), heat-related illness.\n\n"
                "**Prevention:** Stay hydrated, practice good hygiene, avoid crowded sick people, keep cool.\n\n"
                "**Remedy:** Rest, fluids, paracetamol for fever. Seek medical care if fever is very high or persistent."
            )
        elif "cold" in low_lower or "cough" in low_lower:
            bot_reply = (
                "🤧 **Cold / Cough**\n\n"
                "**Causes:** Usually viral respiratory infection.\n\n"
                "**Prevention:** Wash hands, avoid touching face, cover coughs.\n\n"
                "**Remedy:** Rest, warm fluids, honey for cough in adults/children over 1 year; consult a doctor if breathing difficulty."
            )
        elif "headache" in low_lower:
            bot_reply = (
                "🤕 **Headache**\n\n"
                "**Causes:** Stress, dehydration, eyestrain, migraines.\n\n"
                "**Prevention:** Hydrate, regular sleep, manage stress, reduce screen glare.\n\n"
                "**Remedy:** Rest, hydration, OTC pain relief. Seek care if sudden or severe."
            )
        else:
            bot_reply = "I can help with common health topics (fever, cold, headache). Tell me your symptom."

    # ---------- QUANTUM PROFESSOR ----------
    elif feat == "Quantum Professor":
        # determine if steps were requested
        wants_steps = any(k in low_lower for k in ["step", "steps", "step-by-step", "show steps"])
        # calculus detection
        calc = quantum_calculus(low_lower, wants_steps)
        if calc:
            bot_reply = f"🔬 Quantum Calculus\n\n{calc}"
        elif "=" in low:
            try:
                sol_text, sols = quantum_solve_equation(low, wants_steps)
                bot_reply = sol_text
            except Exception:
                bot_reply = "I couldn't parse that equation. Use a clear format like `x^2 - 2*x + 1 = 0`."
        else:
            # treat as expression
            try:
                bot_reply = quantum_details_for_expression(low, wants_steps)
            except Exception:
                bot_reply = "I couldn't parse that expression. Use standard math notation (use ** or ^ for power)."

    # ---------- ASSISTANT (Wikipedia) ----------
    elif feat == "Assistant":
        if low_lower in ("hi", "hello", "hey"):
            bot_reply = "Hello! I am your AI Assistant. Ask about a person, topic, or event."
            st.session_state.last_image = None
            st.session_state.last_link = None
        else:
            try:
                summary = wikipedia.summary(low, sentences=2)
                page = wikipedia.page(low)
                bot_reply = summary
                st.session_state.last_image = page.images[0] if page.images else None
                st.session_state.last_link = page.url
            except wikipedia.DisambiguationError as e:
                options = ", ".join(e.options[:6])
                bot_reply = f"That query is ambiguous. Did you mean: {options}?"
                st.session_state.last_image = None
                st.session_state.last_link = None
            except Exception:
                bot_reply = "Sorry, I couldn't find information on that topic."
                st.session_state.last_image = None
                st.session_state.last_link = None

    # store both global history and current chat (main display)
    st.session_state.history_all.append((feat, "You", user_input))
    st.session_state.current_chat[feat].append(("You", user_input))

    if bot_reply:
        st.session_state.history_all.append((feat, "Bot", bot_reply))
        st.session_state.current_chat[feat].append(("Bot", bot_reply))
        # auto speak only the bot reply
        speak_text_autoplay(bot_reply)

    # mark as processed and clear input box (so user can type fresh)
    st.session_state.last_processed = user_input
    st.session_state.main_input = ""  # clears the text_input (key was "main_input")

# ---------- MAIN DISPLAY: Conversation BELOW input ----------
st.subheader("💬 Conversation")
chat = st.session_state.current_chat.get(st.session_state.current_feature, [])
if not chat:
    st.info("No messages in this conversation yet. Type a message above.")
else:
    for who, txt in chat:
        if who == "You":
            st.markdown(f"**🧑 You:** {txt}")
        else:
            label = {
                "Doctor Help": "AI Doctor",
                "Quantum Professor": "AI Professor",
                "Assistant": "AI Assistant"
            }.get(st.session_state.current_feature, "Bot")
            st.markdown(f"**🤖 {label}:** {txt}")

# ---------- SHOW ASSISTANT IMAGE/LINK (if any) ----------
if st.session_state.current_feature == "Assistant":
    if st.session_state.last_image:
        st.image(st.session_state.last_image, width=220)
    if st.session_state.last_link:
        st.markdown(f"[More Info 🔗]({st.session_state.last_link})")

# ---------- SMALL LIT HEART AT BOTTOM (smaller) ----------
st.markdown("""
    <style>
    .lit-heart {
        position: fixed;
        bottom: 6px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 20px;
        color: red;
        animation: pulse 1s infinite;
        z-index: 9999;
    }
    @keyframes pulse {
        0% { transform: translateX(-50%) scale(1); }
        50% { transform: translateX(-50%) scale(1.12); }
        100% { transform: translateX(-50%) scale(1); }
    }
    </style>
    <div class="lit-heart">❤️</div>
    """, unsafe_allow_html=True)
