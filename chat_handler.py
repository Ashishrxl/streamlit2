import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import threading
import queue
import ast
import re

from utils import convert_df_to_csv


# =====================================================
# ENTERPRISE SECURITY CONFIG
# =====================================================

ALLOWED_IMPORTS = {"pandas", "numpy", "plotly", "matplotlib", "seaborn"}


def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if not any(name.startswith(m) for m in ALLOWED_IMPORTS):
        raise ImportError(f"Import blocked: {name}")
    return __import__(name, globals, locals, fromlist, level)


SAFE_BUILTINS = {
    "len": len,
    "range": range,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "round": round,
    "sorted": sorted,
    "enumerate": enumerate,
    "zip": zip,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "float": float,
    "int": int,
    "str": str,
    "bool": bool,
    "__import__": safe_import
}

EXECUTION_TIMEOUT = 8


# =====================================================
# GEMINI PROMPT BUILDER
# =====================================================

def build_gemini_prompt(prompt, df):

    return f"""
You are a professional Python data analyst.

STRICT RULES:
- Return ONLY Python code inside one fenced block.
- DO NOT include import statements.
- pd, np, px, sns, plt already exist.
- Use dataframe variable name `df`
- Output MUST be stored in:
  result OR df_out OR fig OR output

Columns:
{df.dtypes}

Sample rows:
{df.head(5).to_string()}

User request:
{prompt}
"""


# =====================================================
# AUTO CODE CLEANER
# =====================================================

def clean_generated_code(code):

    cleaned = []

    for line in code.split("\n"):

        if re.match(r"^\s*import\s+", line):
            continue

        if re.match(r"^\s*from\s+.*\s+import\s+", line):
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


# =====================================================
# CODE EXTRACTION
# =====================================================

def extract_python_code(text):

    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text


# =====================================================
# AST SECURITY
# =====================================================

def is_code_safe(code):

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):

            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise ValueError("Import statements not allowed")

            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):
                    if node.func.id in {"exec", "eval", "compile", "open"}:
                        raise ValueError("Unsafe builtin blocked")

                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in {"os", "sys", "subprocess"}:
                            raise ValueError("System access blocked")

    except Exception as e:
        st.error(str(e))
        return False

    return True


# =====================================================
# SANDBOX EXECUTION
# =====================================================

def execute_safe_code(code, df):

    exec_globals = {
        "__builtins__": SAFE_BUILTINS,
        "pd": pd,
        "np": np,
        "px": px,
        "plt": plt,
        "sns": sns,
        "go": go,
        "df": df.copy()
    }

    exec_locals = {}
    result_queue = queue.Queue()

    def runner():
        try:
            exec(code, exec_globals, exec_locals)
            result_queue.put(("success", exec_locals))
        except Exception as e:
            result_queue.put(("error", str(e)))

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join(EXECUTION_TIMEOUT)

    if thread.is_alive():
        return "timeout", None

    return result_queue.get()


# =====================================================
# AUTO REPAIR LAYER
# =====================================================

def attempt_auto_repair(code, error, df, gemini_model):

    repair_prompt = f"""
Fix the Python code below.

Rules:
- No imports
- Keep same logic
- Fix the error: {error}
- Return ONLY corrected Python code

Code:
{code}
"""

    try:
        response = gemini_model.generate_content(repair_prompt)
        repaired_code = extract_python_code(response.text)
        repaired_code = clean_generated_code(repaired_code)
        return repaired_code
    except:
        return None


# =====================================================
# RESULT DISPLAY
# =====================================================

def display_execution_result(obj):

    if isinstance(obj, pd.DataFrame):

        st.dataframe(obj)

        st.download_button(
            "Download CSV",
            convert_df_to_csv(obj),
            "result.csv",
            "text/csv"
        )

    elif isinstance(obj, go.Figure):
        st.plotly_chart(obj, use_container_width=True)

    elif hasattr(obj, "savefig"):
        st.pyplot(obj)

    else:
        st.write(obj)


# =====================================================
# FULL EXECUTION PIPELINE
# =====================================================

def extract_and_execute_code(response_text, df, gemini_model):

    code = extract_python_code(response_text)
    code = clean_generated_code(code)

    st.code(code, language="python")

    if not is_code_safe(code):
        return

    status, payload = execute_safe_code(code, df)

    if status == "success":

        for k in ("result", "df_out", "fig", "output"):
            if k in payload:
                display_execution_result(payload[k])
                return

        st.warning("Code ran but no output variable found")
        return

    if status == "timeout":
        st.error("Execution timed out")
        return

    # -------- AUTO REPAIR --------

    st.warning("Execution failed. Attempting auto repair...")

    repaired_code = attempt_auto_repair(code, payload, df, gemini_model)

    if repaired_code:

        st.code(repaired_code, language="python")

        status2, payload2 = execute_safe_code(repaired_code, df)

        if status2 == "success":
            for k in ("result", "df_out", "fig", "output"):
                if k in payload2:
                    display_execution_result(payload2[k])
                    return

    st.error("Auto repair failed")


# =====================================================
# CHAT UI
# =====================================================

def create_chat_section(tables_dict, gemini_model):

    st.markdown("---")

    with st.expander("🤖 Chat with your CSV"):

        tables = {k: v for k, v in tables_dict.items() if not v.empty}

        if not tables:
            st.warning("No usable tables")
            return

        table_name = st.selectbox("Select table", list(tables.keys()))

        df = tables[table_name].copy()

        st.dataframe(df.head(10))

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [{"role": "assistant", "content": "Ask about your data"}]

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about your data"):

            st.session_state.chat_messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):

                full_prompt = build_gemini_prompt(prompt, df)

                response = gemini_model.generate_content(full_prompt)

                extract_and_execute_code(response.text, df, gemini_model)