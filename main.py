"""
Main application entry point for CSV Visualizer with Forecasting.
"""

import streamlit as st
from streamlit.components.v1 import html
from config import configure_streamlit, configure_gemini_api
from ui_components import (
    create_sidebar_settings, 
    handle_file_upload, 
    run_main_application_logic,
    display_welcome_message
)

# ---- Page Config ----
st.set_page_config(
    page_title="CSV Visualizer & Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Hide Streamlit Branding ----
hide_ui = """
<style>
#MainMenu, footer, header {visibility: hidden;}
[data-testid="stToolbar"], [data-testid="stStatusWidget"] {display: none !important;}
a[href^="https://github.com"], a[href^="https://streamlit.io"] {display: none !important;}
</style>
"""
st.markdown(hide_ui, unsafe_allow_html=True)

# ---- Inject Custom JS to Hide Branding in Parent Frame ----
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

# ---- Modern Animated Background + CSS ----
page_css = """
<style>
body, .stApp {
    background: radial-gradient(circle at top left, #1e3c72, #2a5298);
    font-family: 'Poppins', sans-serif;
    color: #ffffff;
    overflow-x: hidden;
}

/* Title */
.main-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Subtext */
.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: rgba(255,255,255,0.8);
    margin-bottom: 2rem;
}

/* Upload & Content Containers */
.upload-section, .forecast-section {
    background: rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.5rem;
    margin: 1rem auto;
    width: 95%;
    max-width: 1200px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    backdrop-filter: blur(12px);
    transform: translateY(40px);
    opacity: 0;
    transition: all 0.8s ease;
}
.visible {
    transform: translateY(0);
    opacity: 1;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #283e51, #485563);
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Button Enhancements */
.stButton > button {
    background: linear-gradient(90deg, #36d1dc, #5b86e5);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 12px;
    padding: 0.6rem 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}
.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #5b86e5, #36d1dc);
}

/* Chart & DataFrame Styling */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Mobile Responsive */
@media (max-width: 600px) {
    .main-title { font-size: 2rem; }
    .subtitle { font-size: 1rem; }
}
</style>

<script>
document.addEventListener("DOMContentLoaded", function() {
  const boxes = document.querySelectorAll('.upload-section, .forecast-section');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.15 });
  boxes.forEach(box => observer.observe(box));
});
</script>
"""
st.markdown(page_css, unsafe_allow_html=True)


# ---- MAIN FUNCTION ----
def main():
    """Main application function."""
    
    # Configure Streamlit and initialize AI
    configure_streamlit()
    gemini_model = configure_gemini_api()

    # Title + Intro
    st.markdown('<h1 class="main-title">📊 CSV Visualizer & Forecasting</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload your dataset, visualize trends, and forecast with AI-powered precision.</p>', unsafe_allow_html=True)

    # Sidebar settings
    forecast_color, forecast_opacity, show_confidence = create_sidebar_settings()

    # Welcome message
    display_welcome_message()

    # File Upload Section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    file_result = handle_file_upload()
    st.markdown('</div>', unsafe_allow_html=True)

    # Run forecasting logic if file uploaded
    if file_result[0] is not None:
        uploaded_df, is_alldata = file_result
        st.markdown('<div class="forecast-section">', unsafe_allow_html=True)

        run_main_application_logic(
            uploaded_df, 
            is_alldata, 
            forecast_color, 
            forecast_opacity, 
            show_confidence,
            gemini_model
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ---- Run App ----
if __name__ == "__main__":
    main()