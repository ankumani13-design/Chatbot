elif st.session_state.feature == "Quantum Solver":
    input_lower = user_input.lower()
    if "hi" in input_lower or "hello" in input_lower:
        bot_response = "Hi! I am your Quantum Professor. Ask me a math problem or quantum concept."
    
    # ---------- Quantum Functions ----------
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
    
    # ---------- Math Solver ----------
    else:
        try:
            expr = parse_expr(user_input_lower)
            simplified = simplify(expr)
            bot_response = f"✅ Simplified Result: {simplified}"
        except:
            try:
                if "=" in user_input:
                    lhs, rhs = user_input.split("=")
                    x = symbols('x')
                    eq = Eq(parse_expr(lhs), parse_expr(rhs))
                    sol = solve(eq, x)
                    bot_response = f"✅ Solution: {sol}"
                else:
                    bot_response = "Invalid math expression."
            except:
                bot_response = "I couldn't parse the math problem."
