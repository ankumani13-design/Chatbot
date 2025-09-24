# ---------- QUANTUM REPLY FUNCTION ----------
import sympy as sp
from sympy import Matrix
from sympy.physics.quantum import Dagger

def quantum_reply(user_input):
    user_input_lower = user_input.lower()

    # Solve algebraic equations
    if "solve" in user_input_lower:
        try:
            parts = user_input_lower.split("for")
            eq_str = parts[0].replace("solve", "").strip()
            var_str = parts[1].strip()
            var = sp.symbols(var_str)
            eq = sp.sympify(eq_str)
            sol = sp.solve(eq, var)
            return f"Solve {eq} for {var} → Solution: {sol}"
        except:
            return "Please use format: 'Solve <equation> for <variable>'."

    # Differentiate
    elif "differentiate" in user_input_lower:
        try:
            parts = user_input_lower.split("for")
            expr_str = parts[0].replace("differentiate", "").strip()
            var_str = parts[1].strip()
            var = sp.symbols(var_str)
            expr = sp.sympify(expr_str)
            deriv = sp.diff(expr, var)
            return f"Differentiating {expr} w.r.t {var} → Result: {deriv}"
        except:
            return "Use format: 'Differentiate <expression> for <variable>'."

    # Integrate
    elif "integrate" in user_input_lower:
        try:
            parts = user_input_lower.split("for")
            expr_str = parts[0].replace("integrate", "").strip()
            var_str = parts[1].strip()
            var = sp.symbols(var_str)
            expr = sp.sympify(expr_str)
            integ = sp.integrate(expr, var)
            return f"Integrating {expr} w.r.t {var} → Result: {integ}"
        except:
            return "Use format: 'Integrate <expression> for <variable>'."

    # Hermitian conjugate
    elif "dagger" in user_input_lower:
        try:
            expr_str = user_input_lower.replace("dagger", "").strip()
            expr = sp.sympify(expr_str)
            dag = Dagger(expr)
            return f"Hermitian conjugate (dagger) of {expr} → {dag}"
        except:
            return "Error computing dagger."

    # Eigenvalues/eigenvectors
    elif "eigen" in user_input_lower:
        try:
            matrix_str = user_input.split("[",1)[1].rsplit("]",1)[0]
            matrix_list = eval("["+matrix_str+"]")
            mat = Matrix(matrix_list)
            eigenvals = mat.eigenvals()
            eigenvects = mat.eigenvects()
            return f"Eigenvalues: {eigenvals}\nEigenvectors: {eigenvects}"
        except:
            return "Use format: 'Eigen [[a,b],[c,d]]'"

    # Expectation value
    elif "expectation" in user_input_lower:
        try:
            parts = user_input.split("] [")
            matrix_list = eval(parts[0].split("[",1)[1]+"]")
            state_list = eval("["+parts[1].replace("]","")+"]")
            mat = Matrix(matrix_list)
            state = Matrix(state_list)
            val = (state.T * mat * state)[0]
            return f"Expectation value: {val}"
        except:
            return "Use format: 'Expectation [[O]] [state]'"

    # Short theory answers
    else:
        concept = user_input_lower
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
