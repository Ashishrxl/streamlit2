"""
Chat with CSV functionality using Gemini AI.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import re
import ast
import plotly.graph_objs as go
from utils import convert_df_to_csv


def create_chat_section(tables_dict, gemini_model):
    """Create the chat with CSV section."""
    st.markdown("---")
    with st.expander("🤖 Chat with your CSV", expanded=False):
        st.subheader("📌 Select Table for Chat")
        
        available_tables_chat = {k: v for k, v in tables_dict.items() if not v.empty}
        if not available_tables_chat:
            st.warning("⚠️ No usable tables could be derived from the uploaded CSV.")
            st.stop()

        selected_table_name_chat = st.selectbox(
            "Select one table to chat with", 
            list(available_tables_chat.keys()), 
            key="chat_table_select"
        )
        selected_df_chat = available_tables_chat[selected_table_name_chat].copy()

        # Display table preview
        st.write(f"### Preview of '{selected_table_name_chat}'")
        st.dataframe(selected_df_chat.head(10))

        # Initialize and display chat
        initialize_chat_history()
        display_chat_interface(selected_df_chat, gemini_model)


def initialize_chat_history():
    """Initialize chat history for the session."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I can help you analyze this data. What would you like to know?"}
        ]


def display_chat_interface(selected_df_chat, gemini_model):
    """Display the chat interface and handle user interactions."""
    # Display chat messages from history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask me about the data (e.g., 'What's the average amount?')"):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process the user query
        process_user_query(prompt, selected_df_chat, gemini_model)


def process_user_query(prompt, selected_df_chat, gemini_model):
    """Process user query and generate response."""
    # Prepare the prompt for Gemini
    columns_info = ", ".join(selected_df_chat.columns)
    df_sample_str = selected_df_chat.head(5).to_string()

    full_prompt = f"""
You are a data analyst assistant. The user uploaded a pandas DataFrame with these columns:

{selected_df_chat.dtypes.to_string()}

Here are the first 5 rows:

{df_sample_str}

The user asked: {prompt}

Produce a Python-only answer that performs the requested analysis on a pandas DataFrame named `df`.

- Output must contain a single fenced Python code block (``````).
- Do NOT include any import statements (assume pd, np, px, plt, sns are available).
- Use `df` as the variable for the table.
- Put the final result into one of these variables: `result`, `df_out`, `fig`, or `output`.
- Keep code short and focused (prefer <40 lines).
- Do NOT use file, network, or system operations (no open(), no subprocess, no os, no sys).
- If visualization is appropriate, produce a Plotly figure object named `fig`.
"""

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data and requesting Python code from Gemini..."):
            try:
                response = gemini_model.generate_content(full_prompt)
                response_text = response.text.strip()
                
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": "I generated code — attempting to run it safely."
                })

                # Extract and execute code
                extract_and_execute_code(response_text, selected_df_chat)

            except Exception as e:
                st.error(f"❌ An error occurred during chat processing: {e}")
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": "An error occurred while processing your request."
                })


def extract_and_execute_code(response_text, selected_df_chat):
    """Extract Python code from Gemini response and execute it safely."""
    # Extract Python code block from Gemini's response
    code_block = extract_python_code(response_text)
    
    if not code_block:
        st.error("No valid Python code found in the response.")
        return

    st.markdown("**Generated code (preview):**")
    st.code(code_block, language="python")

    # Safety checks
    if not is_code_safe(code_block):
        return

    # Execute code
    execute_safe_code(code_block, selected_df_chat)


def extract_python_code(response_text):
    """Extract Python code block from response text."""
    # Look for `````` first
    m = re.search(r"``````", response_text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        # fallback to any triple backtick block
        m = re.search(r"``````", response_text, flags=re.DOTALL)
    
    if m:
        return m.group(1).strip()
    else:
        # take everything as plain code (last resort)
        return response_text


def is_code_safe(code_block):
    """Perform safety checks on the generated code using AST."""
    unsafe = False
    unsafe_reasons = []

    try:
        tree = ast.parse(code_block)
        for node in ast.walk(tree):
            # Reject imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                unsafe = True
                unsafe_reasons.append("Import statements are not allowed.")

            # Reject calls to dangerous builtins / functions
            if isinstance(node, ast.Call):
                # if function is a simple name
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in {"open", "exec", "eval", "compile", "__import__", "input"}:
                        unsafe = True
                        unsafe_reasons.append(f"Use of builtin `{func_name}` is not allowed.")

                # if function is an attribute like os.system, subprocess.Popen
                if isinstance(node.func, ast.Attribute):
                    root = node.func
                    while isinstance(root, ast.Attribute):
                        root = root.value
                    if isinstance(root, ast.Name):
                        root_name = root.id
                        if root_name in {"os", "sys", "subprocess", "shutil", "socket", "pathlib"}:
                            unsafe = True
                            unsafe_reasons.append(f"Calls to module `{root_name}` are not allowed.")

            # Reject use of Name nodes that access dunders
            if isinstance(node, ast.Name):
                if node.id.startswith("__"):
                    unsafe = True
                    unsafe_reasons.append("Access to dunder names is not allowed.")

            # Reject attribute access like os.*, sys.*, subprocess.* early
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id in {"os", "sys", "subprocess", "shutil", "socket", "pathlib"}:
                    unsafe = True
                    unsafe_reasons.append(f"Attribute access to `{node.value.id}` is not allowed.")

    except Exception as e:
        unsafe = True
        unsafe_reasons.append(f"Failed to parse code: {e}")

    if unsafe:
        st.error("⚠️ The generated code was blocked by safety checks and will NOT be executed.")
        st.markdown("**Reason(s):** " + "; ".join(unsafe_reasons))
        st.info("You can copy the code, inspect/modify it, and run it locally if you trust it.")
        st.session_state.chat_messages.append({
            "role": "assistant", 
            "content": "Generated code was blocked by safety checks and was not executed."
        })
        return False

    return True


def execute_safe_code(code_block, selected_df_chat):
    """Execute code in a restricted namespace."""
    st.info("✅ Code passed safety checks. Executing in a restricted environment...")

    # Prepare restricted environment
    safe_builtins = {
        "len": len, "range": range, "min": min, "max": max, "sum": sum, "abs": abs, 
        "round": round, "sorted": sorted, "str": str, "int": int, "float": float, 
        "dict": dict, "list": list
    }

    # Bind a copy of the dataframe (df) to the environment
    exec_globals = {
        "__builtins__": safe_builtins,
        "pd": pd, "np": np, "px": px, "plt": plt, "sns": sns,
        "df": selected_df_chat.copy()
    }
    exec_locals = {}

    try:
        exec(compile(code_block, "", "exec"), exec_globals, exec_locals)

        # Look for expected output variables
        output_obj = None
        output_name = None
        for name in ("result", "df_out", "fig", "output"):
            if name in exec_locals:
                output_obj = exec_locals[name]
                output_name = name
                break
            if name in exec_globals:
                output_obj = exec_globals[name]
                output_name = name
                break

        if output_obj is None:
            st.warning("The code executed but did not set a recognized output variable (result, df_out, fig, output). Showing full local namespace:")
            st.write({k: type(v).__name__ for k, v in exec_locals.items() if not k.startswith("__")})
            st.session_state.chat_messages.append({
                "role": "assistant", 
                "content": "Code executed but no output variable was found."
            })
        else:
            display_execution_result(output_obj, output_name)

    except Exception as e:
        st.error(f"❌ Error while executing generated code: {e}")
        st.session_state.chat_messages.append({
            "role": "assistant", 
            "content": "There was an error when executing the generated code."
        })


def display_execution_result(output_obj, output_name):
    """Display the result of code execution."""
    # Display results depending on type
    if isinstance(output_obj, pd.DataFrame):
        st.subheader("📄 DataFrame result")
        st.dataframe(output_obj)
        st.download_button(
            "⬇️ Download result (CSV)", 
            data=convert_df_to_csv(output_obj), 
            file_name="chat_code_result.csv", 
            mime="text/csv"
        )
    elif hasattr(output_obj, "to_dict") and not isinstance(output_obj, (str, bytes)):
        # Generic display for things like dicts, series
        try:
            st.subheader("🔎 Result (object)")
            st.write(output_obj)
        except Exception:
            st.write(repr(output_obj))
    else:
        # Plotly figure (plotly.graph_objs._figure.Figure)
        try:
            if isinstance(output_obj, go.Figure):
                st.subheader("📈 Plotly figure result")
                st.plotly_chart(output_obj, use_container_width=True)
            else:
                # Matplotlib figure
                if hasattr(output_obj, "savefig") or hasattr(output_obj, "get_size_inches"):
                    st.subheader("📉 Matplotlib figure result")
                    st.pyplot(output_obj)
                else:
                    st.subheader("📎 Result")
                    st.write(output_obj)
        except Exception:
            # fallback
            st.subheader("📎 Result (fallback)")
            st.write(output_obj)

    # Store assistant message summarizing success
    st.session_state.chat_messages.append({
        "role": "assistant", 
        "content": f"Code executed successfully and produced `{output_name}`."
    })