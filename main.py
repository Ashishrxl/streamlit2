"""
CSV Visualizer & Forecasting — Pastel Light Theme
"""

import streamlit as st
from config import configure_streamlit, configure_gemini_api
from ui_components import (
    create_sidebar_settings, 
    handle_file_upload, 
    run_main_application_logic
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

# --- Modern Pastel Theme CSS ---
page_style = """
<style>
body, .stApp {
    background: linear-gradient(180deg, #f3f9ff, #fdfcff);
    font-family: 'Poppins', sans-serif;
    color: #1a1a1a;
}

/* --- Title --- */
.main-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 800;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #007BFF, #00C6A2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* --- Subtitle --- */
.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: #333;
    opacity: 0.9;
    margin-bottom: 2rem;
}

/* --- Card Container --- */
.card {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 25px;
    box-shadow: 0 6px 15px rgba(0,0,0,0.08);
    padding: 2rem;
    margin: 1.5rem auto;
    width: 90%;
    max-width: 700px;
    text-align: center;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.6);
    transition: transform 0.25s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

/* --- Card Headers with Pastel Gradients --- */
.card-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
    border-radius: 14px;
    padding: 0.8rem 1rem;
    display: inline-block;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.card-header.forecast { background: linear-gradient(90deg, #a18cd1, #fbc2eb); }
.card-header.analysis { background: linear-gradient(90deg, #89f7fe, #66a6ff); }
.card-header.results { background: linear-gradient(90deg, #ffecd2, #fcb69f); }

/* --- Paragraphs --- */
.card p {
    font-size: 1rem;
    color: #222;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

/* --- File Upload Box --- */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(0,0,0,0.2);
    background: rgba(255,255,255,0.9);
    border-radius: 15px;
    transition: all 0.3s ease;
    color: #333 !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #66a6ff;
    background: rgba(255,255,255,1);
    box-shadow: 0 0 12px rgba(102,166,255,0.3);
}
[data-testid="stFileUploaderDropzone"] * {
    color: #333 !important;
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
    box-shadow: 0 4px 10px rgba(91,134,229,0.3);
}
.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #5B86E5, #36D1DC);
}

/* --- Hide Streamlit Defaults --- */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stStatusWidget"] {
    display: none !important;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# --- App Logic ---
def main():
    """Main app function with pastel light-themed UI."""
    configure_streamlit()
    gemini_model = configure_gemini_api()

    # --- Title and subtitle ---
    st.markdown("<h1 class='main-title'>📊 CSV Visualizer & Forecasting</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Upload your dataset, visualize insights, and forecast trends with AI precision.</p>", unsafe_allow_html=True)

    # Sidebar settings
    forecast_color, forecast_opacity, show_confidence = create_sidebar_settings()

    # --- File Upload Section (simple, no card) ---
    file_result = handle_file_upload()

    # --- Show main forecasting card only after upload ---
    if file_result[0] is not None:
        uploaded_df, is_alldata = file_result

        # Forecast Card
        st.markdown("""
        <div class="card">
            <div class="card-header forecast">📈 Forecast & Analyze</div>
            <p>Explore AI-powered forecasting, detect trends, and generate predictive visualizations directly from your dataset.</p>
        </div>
        """, unsafe_allow_html=True)

        # Run main logic
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