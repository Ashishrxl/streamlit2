"""
UI components and interface elements.
"""

import streamlit as st
import pandas as pd
from utils import convert_df_to_csv, convert_df_to_excel
from data_processor import process_alldata_tables, process_regular_tables

from pdf_download import pdfapp


def create_sidebar_settings():
    """Create sidebar with application settings."""
    st.sidebar.header("⚙️ Settings")
    
    forecast_color = st.sidebar.color_picker("Forecast highlight color", "#FFA500")
    forecast_opacity = st.sidebar.slider("Forecast highlight opacity", 0.05, 1.0, 0.12, step=0.01)
    show_confidence = st.sidebar.checkbox("Show confidence interval (upper/lower bounds)", True)
    
    return forecast_color, forecast_opacity, show_confidence


def handle_file_upload():
    """Handle CSV file upload and processing."""
    uploaded_file = st.file_uploader("Upload your CSV file !", type=["csv"])
    

    if uploaded_file is None:
        st.info("Upload a CSV to start. The app will derive tables and let you visualize/forecast.")
        st.stop()

    file_name = uploaded_file.name
    
    if file_name.lower() == "aaabbbccc.csv":
        return process_alldata_file(uploaded_file)
    else:
        return process_regular_file(uploaded_file)


def process_alldata_file(uploaded_file):
    """Process alldata.csv file."""
    try:
        uploaded_df = pd.read_csv(uploaded_file, low_memory=False)
        for col in uploaded_df.select_dtypes(include=['object']).columns:
            uploaded_df[col] = uploaded_df[col].astype(str).str.lower()

        st.success("✅ File uploaded successfully!")
        return uploaded_df, True  # is_alldata=True
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
        st.stop()


def process_regular_file(uploaded_file):
    """Process regular CSV file with structure confirmation."""
    st.warning("⚠️ Please confirm its structure.")
    st.subheader("📋 Confirm File Structure")
    uploaded_df = pd.read_csv(uploaded_file, low_memory=False)
    st.dataframe(uploaded_df)
    
    header_option = st.radio("Does your CSV file have a header row?", ["Yes", "No"])
    
    if header_option == "Yes":
        return process_file_with_header(uploaded_file)
    else:
        return process_file_without_header(uploaded_file)


def process_file_with_header(uploaded_file):
    """Process CSV file that has headers."""
    try:
        uploaded_df = pd.read_csv(uploaded_file, low_memory=False)
        st.dataframe(uploaded_df, low_memory=False)
        st.success("✅ File loaded with header successfully!")
        st.info("Now, please confirm the column names for analysis.")
        
        col_confirm = st.radio("Are the column names correct?", ["Yes", "No, I want to rename them"])
        
        if col_confirm == "Yes":
            st.success("Column names confirmed. Proceeding with visualization and forecasting.")
            return uploaded_df, False  # is_alldata=False
            
        elif col_confirm == "No, I want to rename them":
            return handle_column_renaming(uploaded_df, False)
            
    except Exception as e:
        st.error(f"❌ Error reading CSV with header: {e}")
        st.stop()


def process_file_without_header(uploaded_file):
    """Process CSV file that doesn't have headers."""
    try:
        uploaded_df = pd.read_csv(uploaded_file, header=None, low_memory=False)
        st.success("✅ File loaded without header successfully!")
        st.info("Please rename the generic columns to meaningful names.")
        
        return handle_column_renaming(uploaded_df, True)
        
    except Exception as e:
        st.error(f"❌ Error reading CSV without header: {e}")
        st.stop()


def handle_column_renaming(uploaded_df, is_no_header):
    """Handle column renaming interface."""
    st.info("Please provide the new column names.")
    
    new_cols_dict = {}
    original_cols = uploaded_df.columns.tolist()
    
    for col in original_cols:
        if is_no_header:
            new_name = st.text_input(f"Rename generic column '{col}' (e.g., Column 0):", value="")
        else:
            new_name = st.text_input(f"Rename column '{col}':", value=col)
        new_cols_dict[col] = new_name

    if st.button("Apply Renaming and Analyze"):
        try:
            renamed_df = uploaded_df.rename(columns=new_cols_dict)
            st.success("Columns renamed successfully! Analyzing the new data structure.")
            return renamed_df, False  # is_alldata=False
        except Exception as e:
            st.error(f"❌ Failed to rename columns: {e}")
            st.stop()
    
    # Return None to indicate waiting for user action
    return None, None


def run_main_application_logic(uploaded_df, is_alldata, forecast_color, forecast_opacity, show_confidence, gemini_model):
    """Run the main application logic with all components."""
    # Import here to avoid circular imports
    from data_processor import process_alldata_tables, process_regular_tables, display_tables_preview
    from visualizer import create_visualization_section
    from forecaster import create_forecasting_section
    from chat_handler import create_chat_section
    from filter_df import filter_dataframe
    # Process data into tables
    if is_alldata:
        uploaded_df1 = filter_dataframe(uploaded_df)
        tables_dict = process_alldata_tables(uploaded_df)
        tables_dict["Item-wise"] = uploaded_df1
        with st.expander("Party wise Item List"):
            pdfapp(uploaded_df)
    else:
        tables_dict = process_regular_tables(uploaded_df)
    
    # Display all sections
    display_tables_preview(tables_dict)
    create_visualization_section(tables_dict)
    create_forecasting_section(tables_dict, forecast_color, forecast_opacity, show_confidence)
    create_chat_section(tables_dict, gemini_model)


def display_welcome_message():
    """Display welcome message and instructions."""
    if st.sidebar.button("ℹ️ Show Instructions"):
        with st.expander("📖 How to Use This App", expanded=True):
            st.markdown("""
            ### Welcome to CSV Visualizer with Forecasting!
            
            **Features:**
            1. **📊 Data Visualization** - Create interactive charts and plots
            2. **🔮 Forecasting** - Use Prophet for time series forecasting
            3. **🤖 Chat with CSV** - Ask questions about your data using AI
            
            **Getting Started:**
            1. Upload your CSV file using the file uploader
            2. Confirm the structure and column names if needed
            3. Explore the different sections:
               - **Tables Preview**: View and download processed tables
               - **Visualize Data**: Create various charts and visualizations
               - **Forecasting**: Generate predictions for time series data
               - **Chat with CSV**: Ask AI questions about your data
            
            **Tips:**
            - For forecasting, ensure your data has date and numerical columns
            - Use the sidebar settings to customize forecast visualization
            - The chat feature can generate and execute Python code safely
            """)
