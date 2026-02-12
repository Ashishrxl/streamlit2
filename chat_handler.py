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

ALLOWED_IMPORTS = {
    "pandas",
    "numpy",
    "plotly",
    "matplotlib",
    "seaborn"
}


def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if not any(name.startswith(mod) for mod in ALLOWED_IMPORTS):
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
# CHAT UI
# =====================================================

def create_chat_section(tables_dict, gemini_model):

    st.markdown("---")
    with st.expander("🤖 Chat with your CSV", expanded=False):

        available_tables = {k: v for k, v in tables_dict.items() if not v.empty}

        if not available_tables:
            st.warning("⚠️ No usable tables found")
            return

        table_name = st.selectbox(
            "Select table",
            list(available_tables.keys()),
            key="chat_table_select"
        )

        df = available_tables[table_name].copy()

        st.write(f"### Preview: {table_name}")
        st.dataframe(df.head(10))

        initialize_chat_history()
        display_chat_interface(df, gemini_model)


def initialize_chat_history():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Hello! Ask anything about your data."
            }
        ]


def display_chat_interface(df, gemini_model):

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about your data"):

        st.session_state.chat_messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        process_user_query(prompt, df, gemini_model)


# =====================================================
# GEMINI PROMPT HARDENING
# =====================================================

def build_gemini_prompt(prompt, df):

    return f"""
You are a professional Python data analyst.

STRICT RULES:
- Return ONLY Python code in one fenced block.
- Use dataframe variable name `df`
- No import statements
- No OS, file, subprocess, or network usage
- Final output must be stored in:
  result OR df_out OR fig OR output
- Plotly charts must be stored in fig

Columns:
{df.dtypes}

Sample:
{df.head(5).to_string()}

User Request:
{prompt}
"""


# =====================================================
# USER QUERY PROCESSING
# =====================================================

def process_user_query(prompt, df, gemini_model):

    full_prompt = build_gemini_prompt(prompt, df)

    with st.chat_message("assistant"):
        with st.spinner("Generating analysis..."):

            try:
                response = gemini_model.generate_content(full_prompt)
                response_text = response.text.strip()

                extract_and_execute_code(response_text, df)

            except Exception as e:
                st.error(f"Gemini error: {e}")


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
# AST SECURITY CHECK
# =====================================================

def is_code_safe(code):

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):

            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise ValueError("Import statements are not allowed")

            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):
                    if node.func.id in {"exec", "eval", "compile", "open"}:
                        raise ValueError(f"{node.func.id} not allowed")

                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in {"os", "sys", "subprocess"}:
                            raise ValueError("System calls blocked")

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
        st.error("Execution timed out")
        return

    status, payload = result_queue.get()

    if status == "error":
        st.error(payload)
        return

    for key in ("result", "df_out", "fig", "output"):
        if key in payload:
            display_execution_result(payload[key])
            return

    st.warning("No output variable found")


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
# EXECUTION PIPELINE
# =====================================================

def extract_and_execute_code(response_text, df):

    code = extract_python_code(response_text)

    st.code(code, language="python")

    if not is_code_safe(code):
        return

    execute_safe_code(code, df)