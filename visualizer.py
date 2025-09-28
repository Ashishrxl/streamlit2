"""
Visualization and charting functionality.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from utils import find_col_ci, convert_df_to_csv, convert_df_to_excel, toggle_state, export_plotly_fig, export_matplotlib_fig


def create_visualization_section(tables_dict):
    """Create the main visualization section."""
    st.markdown("---")
    with st.expander("📊 Visualize Data", expanded=False):
        st.subheader("📌 Select Table for Visualization")
        
        available_tables = {k: v for k, v in tables_dict.items() if not v.empty}
        if not available_tables:
            st.warning("⚠️ No usable tables could be derived from the uploaded CSV.")
            st.stop()

        selected_table_name = st.selectbox("Select one table", list(available_tables.keys()))
        selected_df = available_tables[selected_table_name].copy()
        
        # Process data for visualization
        selected_df, date_col_sel = process_data_for_visualization(selected_df)
        
        # Display processed table
        display_processed_table(selected_df, selected_table_name)
        
        # Column selection and visualization
        create_interactive_visualization(selected_df)


def process_data_for_visualization(selected_df):
    """Process and aggregate data for visualization."""
    date_col_sel = find_col_ci(selected_df, "date") or find_col_ci(selected_df, "Date")
    amount_col_sel = find_col_ci(selected_df, "amount") or find_col_ci(selected_df, "Amount")
    name_col_sel = find_col_ci(selected_df, "name") or find_col_ci(selected_df, "Name")

    if date_col_sel:
        try:
            selected_df[date_col_sel] = pd.to_datetime(selected_df[date_col_sel], errors="coerce")
            selected_df = selected_df.sort_values(by=date_col_sel).reset_index(drop=True)
            selected_df['Year_Month'] = selected_df[date_col_sel].dt.to_period('M')
            selected_df['Year'] = selected_df[date_col_sel].dt.to_period('Y')

            numerical_cols = selected_df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = [c for c in selected_df.columns if c not in numerical_cols + ['Year_Month', 'Year', date_col_sel]]

            st.markdown("### 📅 Data Aggregation Options")
            time_period = st.selectbox(
                "Choose time aggregation period:",
                ["No Aggregation", "Monthly", "Yearly"],
                help="Select how you want to aggregate your data over time"
            )

            if time_period != "No Aggregation":
                grouping_options = ["No Grouping"]
                if name_col_sel:
                    grouping_options.append("Group by Name")
                if categorical_cols:
                    grouping_options.append("Group by Custom Columns")

                grouping_choice = st.selectbox(
                    f"Choose {time_period.lower()} grouping method:",
                    grouping_options,
                    help=f"Select how to group your data within each {time_period.lower()} period"
                )

                from data_processor import aggregate_data_by_time
                selected_df, date_col_sel = aggregate_data_by_time(
                    selected_df, date_col_sel, time_period, grouping_choice, 
                    name_col_sel, categorical_cols, numerical_cols
                )
            else:
                st.info("ℹ️ Using original data without time aggregation.")

        except Exception as e:
            st.warning(f"⚠️ Could not process date grouping: {e}")
            st.error(f"Error details: {str(e)}")

    return selected_df, date_col_sel


def display_processed_table(selected_df, selected_table_name):
    """Display processed table with expand/collapse functionality."""
    st.subheader("📋 Selected & Processed Table")
    
    state_key_processed = "expand_processed_table"
    if state_key_processed not in st.session_state:
        st.session_state[state_key_processed] = False

    btn_label_processed = f"Minimise Processed Table" if st.session_state[state_key_processed] else f"Expand Processed Table"
    st.button(btn_label_processed, key="btn_processed_table", on_click=toggle_state, args=(state_key_processed,))

    if st.session_state[state_key_processed]:
        st.write(f"### {selected_table_name} - Processed Table (First 20 Rows)")
        st.dataframe(selected_df.head(20))
        
        with st.expander(f"📖 Show full Processed {selected_table_name} Table"):
            st.markdown("", unsafe_allow_html=True)
            st.dataframe(selected_df)
            
        st.download_button(
            f"⬇️ Download Processed {selected_table_name} (CSV)",
            data=convert_df_to_csv(selected_df),
            file_name=f"processed_{selected_table_name.lower().replace(' ', '')}.csv",
            mime="text/csv",
        )
        
        st.download_button(
            f"⬇️ Download Processed {selected_table_name} (Excel)",
            data=convert_df_to_excel(selected_df),
            file_name=f"processed_{selected_table_name.lower().replace(' ', '')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def create_interactive_visualization(df_vis):
    """Create interactive visualization interface."""
    st.subheader("📌 Column Selection for Visualization")
    
    all_columns = df_vis.columns.tolist()
    default_cols = all_columns.copy() if all_columns else []

    selected_columns = st.multiselect(
        "Select columns to include in visualization (include 'Date' and 'Amount' for forecasting)",
        all_columns,
        default=default_cols,
        help="Choose which columns to include in your analysis and visualization"
    )

    if not selected_columns:
        st.warning("⚠️ Please select at least one column for visualization.")
        st.stop()

    df_vis = df_vis[selected_columns].copy()
    categorical_cols = df_vis.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numerical_cols = df_vis.select_dtypes(include=[np.number]).columns.tolist()

    # Display column metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Columns", len(selected_columns))
    with col2:
        st.metric("Numerical Columns", len(numerical_cols))
    with col3:
        st.metric("Categorical Columns", len(categorical_cols))

    with st.expander("📋 Column Details"):
        st.write("Categorical columns:", categorical_cols if categorical_cols else "None")
        st.write("Numerical columns:", numerical_cols if numerical_cols else "None")

    # Chart creation interface
    create_chart_interface(df_vis, numerical_cols)


def create_chart_interface(df_vis, numerical_cols):
    """Create chart selection and rendering interface."""
    st.subheader("📈 Interactive Visualization")
    
    chart_options = [
        "Scatter Plot", "Line Chart", "Bar Chart", "Histogram", "Correlation Heatmap",
        "Seaborn Scatterplot", "Seaborn Boxplot", "Seaborn Violinplot", "Seaborn Pairplot",
        "Seaborn Heatmap", "Plotly Heatmap", "Treemap", "Sunburst", "Time-Series Decomposition"
    ]

    chart_x_y_hue_req = {
        "Scatter Plot": (True, True, True),
        "Line Chart": (True, True, True),
        "Bar Chart": (True, True, True),
        "Histogram": (True, False, True),
        "Correlation Heatmap": (False, False, False),
        "Seaborn Scatterplot": (True, True, True),
        "Seaborn Boxplot": (True, True, True),
        "Seaborn Violinplot": (True, True, True),
        "Seaborn Pairplot": (False, False, True),
        "Seaborn Heatmap": (False, False, False),
        "Plotly Heatmap": (True, True, False),
        "Treemap": (True, True, False),
        "Sunburst": (True, True, False),
        "Time-Series Decomposition": (True, True, False)
    }

    chart_type = st.selectbox("Select Chart Type", chart_options)
    need_x, need_y, need_hue = chart_x_y_hue_req.get(chart_type, (True, True, False))

    # Column selection for chart
    x_col = y_col = hue_col = None
    
    if need_x:
        x_options = [c for c in df_vis.columns]
        x_col = st.selectbox("Select X Axis", x_options, key="x_axis")

    if need_y:
        y_options = [c for c in df_vis.columns if (c != x_col or not need_x)]
        y_col = st.selectbox("Select Y Axis", y_options, key="y_axis")

    if need_hue:
        hue_options = [c for c in df_vis.columns if c not in [x_col, y_col]]
        hue_col = st.selectbox("Select Hue/Category (optional)", ["(None)"] + hue_options, key="hue_axis")
        if hue_col == "(None)":
            hue_col = None

    # Render chart
    render_chart(df_vis, chart_type, x_col, y_col, hue_col, numerical_cols)


def render_chart(df_vis, chart_type, x_col, y_col, hue_col, numerical_cols):
    """Render the selected chart type."""
    st.write("### Chart:")
    
    try:
        fig = None
        
        # Plotly charts
        if chart_type == "Scatter Plot":
            fig = px.scatter(df_vis, x=x_col, y=y_col, color=hue_col if hue_col else None, title=f"Scatter Plot: {x_col} vs {y_col}")
        elif chart_type == "Line Chart":
            fig = px.line(df_vis, x=x_col, y=y_col, color=hue_col if hue_col else None, title=f"Line Chart: {x_col} vs {y_col}")
        elif chart_type == "Bar Chart":
            fig = px.bar(df_vis, x=x_col, y=y_col, color=hue_col if hue_col else None, title=f"Bar Chart: {x_col} vs {y_col}")
        elif chart_type == "Histogram":
            fig = px.histogram(df_vis, x=x_col, color=hue_col if hue_col else None, title=f"Histogram: {x_col}")
        elif chart_type == "Correlation Heatmap":
            if len(numerical_cols) >= 2:
                corr = df_vis[numerical_cols].corr()
                fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu', aspect='auto', title="Correlation Heatmap")
            else:
                st.warning("⚠️ Need at least 2 numerical columns for correlation heatmap.")
        elif chart_type == "Plotly Heatmap":
            if len(numerical_cols) >= 2:
                fig = px.density_heatmap(df_vis, x=x_col, y=y_col, nbinsx=20, nbinsy=20, title="Plotly Heatmap")
            else:
                st.warning("⚠️ Need at least 2 numerical columns for heatmap.")

        # Display Plotly charts
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
            png_bytes_plotly = export_plotly_fig(fig)
            if png_bytes_plotly:
                st.download_button("⬇️ Download Chart (PNG)", data=png_bytes_plotly, file_name="plotly_chart.png", mime="image/png")

        # Seaborn charts
        if chart_type.startswith("Seaborn"):
            plt.figure(figsize=(10, 6))
            
            if chart_type == "Seaborn Scatterplot":
                sns.scatterplot(data=df_vis, x=x_col, y=y_col, hue=hue_col if hue_col else None)
            elif chart_type == "Seaborn Boxplot":
                sns.boxplot(data=df_vis, x=x_col, y=y_col, hue=hue_col if hue_col else None)
            elif chart_type == "Seaborn Violinplot":
                sns.violinplot(data=df_vis, x=x_col, y=y_col, hue=hue_col if hue_col else None)
            elif chart_type == "Seaborn Pairplot":
                if len(numerical_cols) >= 2:
                    sns.pairplot(df_vis, hue=hue_col if hue_col else None)
            elif chart_type == "Seaborn Heatmap":
                if len(numerical_cols) >= 2:
                    corr = df_vis[numerical_cols].corr()
                    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0)
            
            st.pyplot(plt.gcf())
            png_bytes_mpl = export_matplotlib_fig(plt.gcf())
            st.download_button("⬇️ Download Chart (PNG)", data=png_bytes_mpl, file_name="seaborn_chart.png", mime="image/png")
            plt.close()

    except Exception as e:
        st.error(f"⚠️ Failed to render chart: {e}")