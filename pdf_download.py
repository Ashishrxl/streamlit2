import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

def dataframe_to_pdf(df: pd.DataFrame) -> BytesIO:
    """Convert a DataFrame into a PDF file stored in BytesIO."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Create table data with header
    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def pdfapp(data: pd.DataFrame):
    """Streamlit app to filter dataframe by Name and download Item column as PDF."""

    st.title("Filtered Data PDF Exporter")

    # Ensure 'Name' column exists
    if "Name" not in data.columns or "Item" not in data.columns:
        st.error("DataFrame must contain 'Name' and 'Item' columns")
        return

    # Unique names list
    names = data["Name"].dropna().unique().tolist()

    selected_name = st.selectbox("Choose a Name", names)

    if selected_name:
        filtered_df = data.loc[data["Name"] == selected_name, ["Item"]]

        st.write("### Filtered DataFrame")
        st.dataframe(filtered_df)

        pdf_buffer = dataframe_to_pdf(filtered_df)

        with st.expander("Download PDF"):
            st.download_button(
                label="Download filtered data as PDF",
                data=pdf_buffer,
                file_name=f"filtered_{selected_name}.pdf",
                mime="application/pdf",
            )