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

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stStatusWidget"] {display: none;}
[data-testid="stToolbar"] {display: none;}
a[href^="https://github.com"] {display: none !important;}
a[href^="https://streamlit.io"] {display: none !important;}

/* The following specifically targets and hides all child elements of the header's right side,
   while preserving the header itself and, by extension, the sidebar toggle button. */
header > div:nth-child(2) {
    display: none;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



def main():
    """Main application function."""
    # Configure Streamlit and initialize AI
    configure_streamlit()
    gemini_model = configure_gemini_api()
    
    # Create sidebar settings
    forecast_color, forecast_opacity, show_confidence = create_sidebar_settings()
    
    # Display welcome message
    display_welcome_message()
    
    # Handle file upload and processing
    file_result = handle_file_upload()
    
    # Check if we got a valid result (not waiting for user input)
    if file_result[0] is not None:
        uploaded_df, is_alldata = file_result
        
        # Run main application logic
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
