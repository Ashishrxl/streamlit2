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

# --- CSS for Full Modern UI ---
page_css = """
<style>
body, .stApp {
    background: radial-gradient(circle at top left, #16213e, #1a2a6c);
    font-family: 'Poppins', sans-serif;
    color: #ffffff;
    overflow-x: hidden;
}

/* Title */
.main-title {
    text-align: center;
    font-size: 2.4rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    margin-top: 1rem;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: rgba(255,255,255,0.85);
    margin-bottom: 2rem;
}

/* Upload & Forecast Panels */
.upload-section, .forecast-section {
    background: rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 1.8rem;
    margin: 2rem auto;
    width: 95%;
    max-width: 1200px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    backdrop-filter: blur(12px);
    transform: translateY(40px);
    opacity: 0;
    transition: all 0.8s ease;
}
.visible {
    transform: translateY(0);
    opacity: 1;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #283e51, #485563);
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Buttons */
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

/* File Upload Widget */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(255,255,255,0.5);
    background: rgba(255,255,255,0.07);
    border-radius: 15px;
    transition: all 0.3s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #36d1dc;
    box-shadow: 0 0 15px #36d1dc;
    background: rgba(255,255,255,0.15);
    animation: pulseGlow 1.5s infinite;
}

/* Glow Pulse Animation */
@keyframes pulseGlow {
  0% { box-shadow: 0 0 0px rgba(54,209,220,0.3); }
  50% { box-shadow: 0 0 15px rgba(54,209,220,0.8); }
  100% { box-shadow: 0 0 0px rgba(54,209,220,0.3); }
}

/* Fade-in Animation */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Mobile View */
@media (max-width: 600px) {
    .main-title { font-size: 1.8rem; }
    .subtitle { font-size: 0.95rem; }
    .upload-section, .forecast-section { padding: 1rem; margin: 1rem; }
}

/* Hide Streamlit Branding */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stStatusWidget"], [data-testid="stActionButton"] {
    display: none !important;
}
a[href^="https://github.com"], a[href^="https://streamlit.io"] {
    display: none !important;
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


# --- Main Application ---
def main():
    """Main application function."""
    configure_streamlit()
    gemini_model = configure_gemini_api()

    # Header
    st.markdown("<h1 class='main-title'>📈 CSV Visualizer & Forecasting</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Upload your dataset, visualize trends, and forecast with AI-powered precision.</p>", unsafe_allow_html=True)

    # Sidebar
    forecast_color, forecast_opacity, show_confidence = create_sidebar_settings()

    # Welcome Message
    display_welcome_message()

    # Upload Section
    with st.container():
        st.markdown("<div class='upload-section visible'>", unsafe_allow_html=True)
        st.subheader("📤 Upload your CSV file")
        file_result = handle_file_upload()
        st.markdown("</div>", unsafe_allow_html=True)

    # If file uploaded, run logic
    if file_result[0] is not None:
        uploaded_df, is_alldata = file_result
        st.markdown("<div class='forecast-section visible'>", unsafe_allow_html=True)
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