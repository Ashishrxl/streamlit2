"""
Modern CSV Visualizer with Forecasting — Gradient Card Design
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
html("""
<script>
try {
    const sel = window.top.document.querySelectorAll('[href*="streamlit.io"], [href*="streamlit.app"]');
    sel.forEach(e => e.style.display='none');
} catch(e) { console.warn('parent DOM not reachable', e); }
</script>
""", height=0)

# --- Page Configuration ---
st.set_page_config(page_title="CSV Visualizer & Forecasting", page_icon="📊", layout="centered")

# --- Custom Modern CSS ---
page_style = """
<style>
body, .stApp {
    background: linear-gradient(180deg, #061C36, #0A2A43, #113A5D);
    font-family: 'Poppins', sans-serif;
    color: #F5F7FA;
}

/* --- Page Title --- */
.main-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 800;
    margin-top: 1rem;
    margin-bottom: 0.4rem;
    background: linear-gradient(90deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* --- Subtitle --- */
.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 2rem;
}

/* --- Gradient Card Container --- */
.card {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.12));
    border-radius: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    padding: 2rem;
    margin: 1.5rem auto;
    width: 90%;
    max-width: 700px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.25s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: scale(1.03);
    box-shadow: 0 10px 35px rgba(0,0,0,0.4);
}

/* --- Gradient Header for Each Section --- */
.card-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(90deg, #36D1DC, #5B86E5);
    border-radius: 14px;
    padding: 0.8rem 1rem;
    display: inline-block;
    margin-bottom: 1rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}
.card-header.upload { background: linear-gradient(90deg, #F7971E, #FFD200); }
.card-header.forecast { background: linear-gradient(90deg, #8E2DE2, #4A00E0); }
.card-header.settings { background: linear-gradient(90deg, #00DBDE, #FC00FF); }

/* --- Paragraphs --- */
.card p {
    font-size: 1rem;
    color: rgba(255,255,255,0.95);
    margin-bottom: 1.5rem;
}

/* --- File Upload Box --- */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(255,255,255,0.4);
    background: rgba(255,255,255,0.06);
    border-radius: 15px;
    transition: all 0.3s ease;
    color: #fff !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #00C9FF;
    background: rgba(255,255,255,0.15);
    box-shadow: 0 0 15px rgba(0,201,255,0.8);
}
[data-testid="stFileUploaderDropzone"] * {
    color: #f0f0f0 !important;
}

/* --- Buttons --- */
.stButton > button {
    background: linear-gradient(90deg, #36D1DC, #5B86E5);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #5B86E5, #36D1DC);
}

/* --- Hide Streamlit Default Elements --- */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stStatusWidget"] {
    display: none !important;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# --- App Content ---
def main():
    """Main modern application layout."""
    configure_streamlit()
    gemini_model = configure_gemini_api()

    # Title and subtitle
    st.markdown("<h1 class='main-title'>🌐 CSV Visualizer & Forecasting</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Upload your dataset, visualize insights, and forecast trends with AI precision.</p>", unsafe_allow_html=True)

    # Sidebar Settings
    forecast_color, forecast_opacity, show_confidence = create_sidebar_settings()

    # Welcome Card
    st.markdown("""
    <div class="card">
        <div class="card-header settings">⚙️ Welcome</div>
        <p>Start by uploading your CSV file below. Configure your chart and forecast settings easily in the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)
    display_welcome_message()

    # Upload Card
    st.markdown("""
    <div class="card">
        <div class="card-header upload">📤 Upload CSV File</div>
        <p>Upload your CSV file to start visualizing data and generating forecasts.</p>
    </div>
    """, unsafe_allow_html=True)
    file_result = handle_file_upload()

    # Forecast Card (if file uploaded)
    if file_result[0] is not None:
        uploaded_df, is_alldata = file_result
        st.markdown("""
        <div class="card">
            <div class="card-header forecast">📈 Forecast & Analyze</div>
            <p>View insights, visualize trends, and explore AI-powered forecasting results.</p>
        </div>
        """, unsafe_allow_html=True)
        run_main_application_logic(
            uploaded_df, 
            is_alldata, 
            forecast_color, 
            forecast_opacity, 
            show_confidence,
            gemini_model
        )

if __name__ == "__main__":
    main()