# CSV Visualizer with Forecasting

A comprehensive Streamlit application for CSV data analysis, visualization, and forecasting with AI-powered chat functionality.

## Features

- **📊 Data Visualization**: Create interactive charts using Plotly and Seaborn
- **🔮 Forecasting**: Time series forecasting using Prophet
- **🤖 Chat with CSV**: AI-powered data analysis using Google Gemini
- **📈 Multiple Chart Types**: Scatter plots, line charts, bar charts, heatmaps, and more
- **📋 Table Processing**: Automatic table derivation and data processing
- **💾 Export Options**: Download data and visualizations in various formats

## Project Structure

├── main.py                 # Main application entry point
├── config.py              # Configuration and imports
├── utils.py               # Utility functions
├── data_processor.py      # Data processing and table generation
├── visualizer.py          # Visualization functionality
├── forecaster.py          # Forecasting using Prophet
├── chat_handler.py        # AI chat functionality
├── ui_components.py       # UI components and interface
├── requirements.txt       # Project dependencies
└── README.md             # This file
---

## Installation

1. Clone this repository or download the files.

2. Install the required dependencies:
pip install -r requirements.txt
3. Set up your Google AI API key in Streamlit secrets:

- Create a `.streamlit/secrets.toml` file in your project directory
- Add your API key like this:
GOOGLE_API_KEY = "your-api-key-here"
---

## Usage

Run the application using Streamlit:
streamlit run main.py
---

## Modules Overview

### main.py

The main entry point that orchestrates all components and handles the application flow.

### config.py

Contains all imports and configuration settings for the application, including Streamlit page setup and Gemini AI configuration.

### utils.py

Utility functions for:

- Data conversion (CSV, Excel)
- Figure export (PNG)
- Column finding with case-insensitive matching
- State management

### data_processor.py

Handles data processing tasks:

- Processing alldata.csv structure into normalized tables
- Regular CSV file processing
- Data aggregation by time periods
- Table preview and download functionality

### visualizer.py

Manages all visualization functionality:

- Interactive chart creation
- Support for Plotly and Seaborn charts
- Data aggregation options
- Chart export functionality

### forecaster.py

Implements forecasting capabilities:

- Prophet model integration
- Time series forecasting
- Forecast visualization
- Statistical summaries

### chat_handler.py

AI-powered chat functionality:

- Integration with Google Gemini
- Safe code execution
- Dynamic data analysis
- Interactive queries

### ui_components.py

User interface components:

- File upload handling
- Settings sidebar
- Column renaming interface
- Welcome messages and instructions

---

## File Types Supported

- **CSV files**: Primary data format
- **Special handling for "alldata.csv"**: Automatic table normalization
- **Header/No-header support**: Flexible CSV structure handling

---

## Security Features

- **Safe code execution**: AST-based code analysis
- **Restricted environment**: Limited access to system functions
- **Input validation**: Comprehensive safety checks

---

## Dependencies

See `requirements.txt` for a complete list of dependencies including:

- Streamlit for the web interface
- Pandas and NumPy for data manipulation
- Plotly and Seaborn for visualization
- Prophet for forecasting
- Google GenerativeAI for chat functionality

---

## Contributing

This modular structure makes it easy to:

- Add new visualization types in `visualizer.py`
- Extend forecasting methods in `forecaster.py`
- Improve data processing in `data_processor.py`
- Add new UI components in `ui_components.