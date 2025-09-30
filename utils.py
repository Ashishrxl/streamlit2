"""
Utility functions for data conversion and helper operations.
"""

import pandas as pd
import io
import streamlit as st
import plotly.io as pio





def find_col_ci(df: pd.DataFrame, target: str):
    """Find column by case-insensitive name matching."""
    for c in df.columns:
        if c.lower() == target.lower():
            return c
    return None


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel bytes."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return buffer.getvalue()


def export_plotly_fig(fig):
    """Export Plotly figure to PNG bytes."""
    try:
        return pio.to_image(fig, format="png", engine="kaleido")
    except Exception:
        return None


def export_matplotlib_fig(fig):
    """Export Matplotlib figure to PNG bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()


def toggle_state(key):
    """Toggle boolean state in Streamlit session state."""
    st.session_state[key] = not st.session_state[key]






