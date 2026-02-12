import streamlit as st
import pandas as pd
import numpy as np
import ast
import builtins
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# =========================================================
# CONFIG
# =========================================================

EXECUTION_TIMEOUT = 5  # seconds

ALLOWED_IMPORTS = {
    "pandas",
    "numpy",
    "plotly",
    "plotly.express",
    "plotly.graph_objects",
    "matplotlib.pyplot",
    "seaborn"
}

BLOCKED_NAMES = {
    "open",
    "exec",
    "eval",
    "compile",
    "__import__",
    "input",
    "os",
    "sys",
    "subprocess",
    "socket",
    "requests",
    "shutil",
    "pathlib"
}

# =========================================================
# AST SECURITY VALIDATOR
# =========================================================

class SecurityVisitor(ast.NodeVisitor):

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name not in ALLOWED_IMPORTS:
                raise ValueError(f"Blocked import: {alias.name}")

    def visit_ImportFrom(self, node):
        if node.module not in ALLOWED_IMPORTS:
            raise ValueError(f"Blocked import from: {node.module}")

    def visit_Name(self, node):
        if node.id in BLOCKED_NAMES:
            raise ValueError(f"Blocked usage: {node.id}")

def validate_code(code):
    tree = ast.parse(code)
    SecurityVisitor().visit(tree)

# =========================================================
# SAFE BUILTINS
# =========================================================

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
    "bool": bool
}

# =========================================================
# OUTPUT DISPLAY
# =========================================================

def display_execution_result(output, name):

    if isinstance(output, pd.DataFrame):
        st.dataframe(output)

    elif isinstance(output, plotly.graph_objs._figure.Figure):
        st.plotly_chart(output, use_container_width=True)

    elif isinstance(output, plt.Figure):
        st.pyplot(output)

    else:
        st.write(output)

# =========================================================
# EXECUTION SANDBOX
# =========================================================

def execute_safe_code(code, df):

    validate_code(code)

    safe_globals = {
        "__builtins__": SAFE_BUILTINS,
        "pd": pd,
        "np": np,
        "px": px,
        "go": go,
        "plotly": plotly,
        "plt": plt,
        "sns": sns,
        "make_subplots": make_subplots,
        "df": df.copy()
    }

    safe_locals = {}

    def run():
        exec(compile(code, "", "exec"), safe_globals, safe_locals)

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run)
            future.result(timeout=EXECUTION_TIMEOUT)

        # Search outputs
        for name in ("result", "df_out", "fig", "output"):
            if name in safe_locals:
                display_execution_result(safe_locals[name], name)
                return
            if name in safe_globals:
                display_execution_result(safe_globals[name], name)
                return

        st.warning("Code executed but no output variable found.")

    except TimeoutError:
        st.error("Execution stopped (timeout).")

    except Exception as e:
        st.error(f"Execution error: {e}")

# =========================================================
# STREAMLIT UI
# =========================================================

st.title("🔐 Enterprise AI Code Sandbox")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    st.success("Dataset Loaded")
    st.dataframe(df.head())

    code = st.text_area(
        "Paste AI Generated Python Code",
        height=300
    )

    if st.button("Run Code"):
        execute_safe_code(code, df)