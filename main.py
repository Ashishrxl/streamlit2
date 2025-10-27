"""
Main application entry point for CSV Visualizer with Forecasting.
"""

import streamlit as st
from config import configure_streamlit, configure_gemini_api
from ui_components import (
    create_sidebar_settings, 
    handle_file_upload, 
    run_main_application_logic,
    display_welcome_message
)

from streamlit.components.v1 import html

# --- Hide Streamlit Branding ---
html(
    """
    <script>
    try {
        const sel = window.top.document.querySelectorAll('[href*="streamlit.io"], [href*="streamlit.app"]');
        sel.forEach(e => e.style.display='none');
    } catch(e) { console.warn('parent DOM not reachable', e); }
    </script>
    """,
    height=0
)

# --- Modern, clean, glassmorphic CSS ---
page_css = """
<style>
body, .stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    font-family: 'Poppins', sans-serif;
    color: #ffffff;
    overflow-x: hidden;
}

/* --- Page Title --- */
.main-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 800;
    margin-top: 1.2rem;
    margin-bottom: 0.3rem;
    background: linear-gradient(90deg, #00c9ff, #92fe9d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* --- Subtitle --- */
.subtitle {
    text-align: center;
    font-size: 1.1rem;
    font-weight: 400;
    color: rgba(255, 255, 255, 0.85);
    margin-bottom: 2.2rem;
}

/* --- Section Container --- */
.section {
    background: rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem auto;
    width: 95%;
    max-width: 950px;
    box-shadow: 0 4px 25px rgba(0,0,0,0.25);
    backdrop-filter: blur(10px);
    animation: fadeIn 0.8s ease forwards;
}

/* --- Section Header --- */
.section h3 {
    font-size: 1.3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00dbde, #fc00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* --- Upload Box Styling --- */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(255,255,255,0.45);
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 1rem;
    transition: all 0.3s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #00dbde;
    box-shadow: 0 0 15px #00dbde;
    background: rgba(255,255,255,0.12);
    animation: pulseGlow 1.6s infinite;
}

/* --- Buttons --- */
.stButton > button {
    background: linear-gradient(90deg, #36d1dc, #5b86e5);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #5b86e5, #36d1dc);
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #243b55, #141e30);
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* --- Animations --- */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(25px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
  0% { box-shadow: 0 0 0 rgba(0,219,222,0.3); }
  50% { box-shadow: 0 0 18px rgba(0,219,222,0.8); }
  100% { box-shadow: 0 0 0 rgba(0,219,222,0.3); }
}

/* --- Mobile View --- */
@media (max-width: 600px) {
    .main-title { font-size: 1.9rem; }
    .subtitle { font-size: 1rem; margin-bottom: 1.5rem; }
    .section { padding: 1.3rem; margin: 1rem; }
    h3 { font-size: 1.15rem; }
}

/* --- Hide Streamlit Default Elements --- */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stStatusWidget"], [data-testid="stActionButton"] {
    display: none !important;
}
a[href^="https://github.com"], a[href^="https://streamlit.io"] {
    display: none !important;
}
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)

# --- Main Application ---
def main():
    """Main application function."""
    configure_streamlit()
    gemini_model = configure_gemini_api()

    # Header
    st.markdown("<h1 class='main-title'>📊 CSV Visualizer & Forecasting</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Upload your dataset, visualize insights, and forecast trends with AI precision.</p>", unsafe_allow_html=True)

    # Sidebar Settings
    forecast_color, forecast_opacity, show_confidence = create_sidebar_settings()

    # Welcome Message (from UI components)
    display_welcome_message()

    # Upload Section
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<h3>📤 Upload your CSV File</h3>", unsafe_allow_html=True)
    file_result = handle_file_upload()
    st.markdown("</div>", unsafe_allow_html=True)

    # Forecast Section (only after upload)
    if file_result[0] is not None:
        uploaded_df, is_alldata = file_result
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<h3>📈 Forecast & Analyze</h3>", unsafe_allow_html=True)
        run_main_application_logic(
            uploaded_df, 
            is_alldata, 
            forecast_color, 
            forecast_opacity, 
            show_confidence,
            gemini_model
        )
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()