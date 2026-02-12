"""
Chat with CSV using Gemini AI
Streamlit Safe + Secure Sandbox + Smart Prompt
"""

import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import re
import ast
import plotly.graph_objs as go

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from utils import convert_df_to_csv


# ============================================================
# SECURITY CONFIG
# ============================================================

ALLOWED_MODULES = {
    "pandas",
    "numpy",
    "plotly",
    "plotly.express",
    "matplotlib.pyplot",
    "seaborn"
}

BLOCKED_ROOT_MODULES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "requests",
    "urllib",
    "http",
    "ftplib",
    "paramiko"
}


# ============================================================
# GEMINI PROMPT BUILDER
# ============================================================

def build_gemini_prompt(user_prompt, df):

    df_sample = df.head(5).to_string()
    df_types = df.dtypes.to_string()

    return f"""
You are an expert senior data analyst working inside a secure analytics sandbox.

You are given a pandas DataFrame named `df`.

------------------------------------------------
DATAFRAME INFORMATION
------------------------------------------------

Column types:
{df_types}

Sample rows:
{df_sample}

------------------------------------------------
USER QUESTION
------------------------------------------------
{user_prompt}

------------------------------------------------
STRICT RULES
------------------------------------------------

1. Output ONLY Python code inside ONE fenced block.
2. No explanations.
3. No import statements.
4. Never access files, OS, or network.
5. Use ONLY dataframe named df.
6. Prefer vectorized pandas operations.
7. Avoid loops unless absolutely required.
8. Keep code under 40 lines.
9. Handle missing values safely.
10. Do NOT modify df in-place unless required.

------------------------------------------------
OUTPUT REQUIREMENTS
------------------------------------------------

Store final output in ONE of:

result
df_out
fig
output

------------------------------------------------
VISUALIZATION RULES
------------------------------------------------

If chart is useful:
- Use Plotly Express
- Assign chart to variable `fig`
- Add labels + title
"""


# ============================================================
# STREAMLIT UI
# ============================================================

def create_chat_section(tables_dict, gemini_model):

    st.markdown("---")

    with st.expander("🤖 Chat with your CSV"):

        available_tables = {k: v for k, v in tables_dict.items() if not v.empty}

        if not available_tables:
            st.warning("No usable tables found.")
            return

        selected_name = st.selectbox("Select table", list(available_tables.keys()))

        df = available_tables[selected_name].copy()

        st.write(f"Preview: {selected_name}")
        st.dataframe(df.head(10))

        initialize_chat_history()
        display_chat_interface(df, gemini_model)


# ============================================================
# CHAT
# ============================================================

def initialize_chat_history():

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Ask me about your data."}
        ]


def display_chat_interface(df, gemini_model):

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about your data"):

        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        process_user_query(prompt, df, gemini_model)


# ============================================================
# QUERY PROCESSING
# ============================================================

def process_user_query(prompt, df, gemini_model):

    full_prompt = build_gemini_prompt(prompt, df)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):

            try:
                response = gemini_model.generate_content(full_prompt)
                response_text = response.text.strip()

                extract_and_execute_code(response_text, df)

            except Exception as e:
                st.error(e)


# ============================================================
# CODE EXTRACTION
# ============================================================

def extract_and_execute_code(response_text, df):

    code_block = extract_python_code(response_text)

    if not code_block:
        st.error("No python code detected.")
        return

    st.markdown("Generated Code")
    st.code(code_block, language="python")

    if not is_code_safe(code_block):
        return

    execute_safe_code(code_block, df)


def extract_python_code(text):

    match = re.search(r"```python(.*?)```", text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    match = re.search(r"```(.*?)```", text, re.DOTALL)

    return match.group(1).strip() if match else text


# ============================================================
# AST SECURITY VALIDATION
# ============================================================

def is_code_safe(code_block):

    try:
        tree = ast.parse(code_block)

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in ALLOWED_MODULES:
                        st.error(f"Import '{alias.name}' blocked")
                        return False

            if isinstance(node, ast.ImportFrom):
                if node.module not in ALLOWED_MODULES:
                    st.error(f"Import from '{node.module}' blocked")
                    return False

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"open", "exec", "eval", "compile", "__import__"}:
                        st.error(f"Function '{node.func.id}' blocked")
                        return False

            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id in BLOCKED_ROOT_MODULES:
                        st.error(f"Access to '{node.value.id}' blocked")
                        return False

    except Exception as e:
        st.error(f"Validation error: {e}")
        return False

    return True


# ============================================================
# SAFE EXECUTION (Thread Timeout Version)
# ============================================================

def execute_safe_code(code_block, df):

    st.info("Running inside secure sandbox")

    safe_globals = {

        "__builtins__": {
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
            "bool": bool
        },

        "pd": pd,
        "np": np,
        "px": px,
        "plt": plt,
        "sns": sns,
        "df": df.copy()
    }

    safe_locals = {}

    def run_code():
        exec(compile(code_block, "", "exec"), safe_globals, safe_locals)

    try:

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_code)
            future.result(timeout=5)

        output_obj = None
        output_name = None

        for name in ("result", "df_out", "fig", "output"):
            if name in safe_locals:
                output_obj = safe_locals[name]
                output_name = name
                break
            if name in safe_globals:
                output_obj = safe_globals[name]
                output_name = name
                break

        if output_obj is None:
            st.warning("Code executed but no output variable found.")
            return

        display_execution_result(output_obj, output_name)

    except TimeoutError:
        st.error("Execution stopped due to timeout")

    except Exception as e:
        st.error(f"Execution error: {e}")


# ============================================================
# RESULT DISPLAY
# ============================================================

def display_execution_result(output_obj, output_name):

    if isinstance(output_obj, pd.DataFrame):

        st.subheader("DataFrame Result")
        st.dataframe(output_obj)

        st.download_button(
            "Download CSV",
            convert_df_to_csv(output_obj),
            file_name="result.csv"
        )

    elif isinstance(output_obj, go.Figure):

        st.subheader("Plotly Chart")
        st.plotly_chart(output_obj, use_container_width=True)

    elif hasattr(output_obj, "savefig"):

        st.subheader("Matplotlib Chart")
        st.pyplot(output_obj)

    else:
        st.subheader("Result")
        st.write(output_obj)