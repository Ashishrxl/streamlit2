"""
Configuration and imports for the CSV Visualizer application.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from prophet import Prophet
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import io
import google.generativeai as genai
import json
import re
import ast
import plotly.graph_objs as go

# Application configuration
APP_TITLE = "CSV Visualizer with Forecasting (Interactive)"
APP_ICON = "📊"

def configure_streamlit():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide"
    )
    
    st.title(f"{APP_ICON} {APP_TITLE}")
    
    # Hide Streamlit style
    hide_streamlit_style = """"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def configure_gemini_api():
    """Configure Gemini AI API."""
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        return gemini_model
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}. Please ensure GOOGLE_API_KEY is set in your Streamlit secrets.")
        st.stop()
        return None