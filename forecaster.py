"""
Forecasting functionality using Prophet.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from utils import find_col_ci, convert_df_to_csv, convert_df_to_excel, export_plotly_fig


def create_forecasting_section(tables_dict, forecast_color, forecast_opacity, show_confidence):
    """Create the main forecasting section."""
    st.markdown("---")
    with st.expander("🔮 Forecasting", expanded=False):
        st.subheader("📌 Select Table for Forecasting")
        
        available_tables = {k: v for k, v in tables_dict.items() if not v.empty}
        if not available_tables:
            st.warning("⚠️ No usable tables could be derived from the uploaded CSV.")
            st.stop()

        selected_table_name_forecast = st.selectbox(
            "Select one table for forecasting", 
            list(available_tables.keys()), 
            key="forecast_table_select"
        )
        selected_df_forecast = available_tables[selected_table_name_forecast].copy()

        # Identify date and numerical columns
        date_columns = [c for c in selected_df_forecast.columns if "date" in c.lower() or c.lower() in ["year_month", "year"]]
        numerical_cols = selected_df_forecast.select_dtypes(include=[np.number]).columns.tolist()

        if date_columns and numerical_cols:
            process_forecasting_data(
                selected_df_forecast, date_columns, numerical_cols, 
                forecast_color, forecast_opacity, show_confidence
            )
        else:
            st.info("ℹ️ The selected table does not contain a valid date column and/or a numerical column for forecasting.")


def process_forecasting_data(selected_df_forecast, date_columns, numerical_cols, forecast_color, forecast_opacity, show_confidence):
    """Process data and create forecasting interface."""
    st.markdown("---")
    st.subheader("🔮 Forecasting Options")

    selected_date_col = st.selectbox("Select Date Column for Forecasting", date_columns)
    selected_amount_col = st.selectbox("Select Numerical Column for Forecasting", numerical_cols)

    if selected_date_col and selected_amount_col:
        # Prepare forecast data
        forecast_df = selected_df_forecast[[selected_date_col, selected_amount_col]].copy()
        forecast_df[selected_date_col] = pd.to_datetime(forecast_df[selected_date_col], errors="coerce")
        forecast_df[selected_amount_col] = pd.to_numeric(forecast_df[selected_amount_col], errors="coerce")
        forecast_df = forecast_df.dropna(subset=[selected_date_col, selected_amount_col])

        # Aggregation options
        aggregation_period = st.selectbox("Select Aggregation Period", ["No Aggregation", "Monthly", "Yearly"])
        
        if aggregation_period != "No Aggregation":
            if aggregation_period == "Monthly":
                forecast_df = forecast_df.groupby(pd.Grouper(key=selected_date_col, freq='M')).sum(numeric_only=True).reset_index()
                freq_str = "M"
                period_type = "months"
            else:
                forecast_df = forecast_df.groupby(pd.Grouper(key=selected_date_col, freq='Y')).sum(numeric_only=True).reset_index()
                freq_str = "Y"
                period_type = "years"
        else:
            freq_str = "M"
            period_type = "months"

        # Run forecasting
        run_forecasting_model(
            forecast_df, selected_date_col, selected_amount_col, 
            freq_str, period_type, forecast_color, forecast_opacity, show_confidence
        )


def run_forecasting_model(forecast_df, selected_date_col, selected_amount_col, freq_str, period_type, forecast_color, forecast_opacity, show_confidence):
    """Run the Prophet forecasting model."""
    original_forecast_df = forecast_df.copy()
    forecast_df = forecast_df.rename(columns={selected_date_col: "ds", selected_amount_col: "y"})

    min_data_points = 3
    if len(forecast_df) >= min_data_points:
        st.write(f"📈 **Forecasting based on {len(forecast_df)} data points**")

        # Forecast horizon selection
        col1, col2 = st.columns(2)
        with col1:
            if freq_str == "Y":
                horizon = st.slider(f"Forecast Horizon ({period_type})", 1, 10, 3)
            else:
                horizon = st.slider(f"Forecast Horizon ({period_type})", 3, 24, 6)

        with col2:
            st.write(f"**Data range:** {forecast_df['ds'].min().strftime('%Y-%m-%d')} to {forecast_df['ds'].max().strftime('%Y-%m-%d')}")

        # Run Prophet model
        with st.spinner("🔄 Running forecast model..."):
            prophet_model = Prophet()
            prophet_model.fit(forecast_df)

            future = prophet_model.make_future_dataframe(periods=horizon, freq=freq_str)
            forecast = prophet_model.predict(future)

            # Separate historical and future forecasts
            last_date = forecast_df["ds"].max()
            hist_forecast = forecast[forecast["ds"] <= last_date]
            future_forecast = forecast[forecast["ds"] > last_date]

            # Create forecast visualization
            create_forecast_visualization(
                original_forecast_df, selected_date_col, selected_amount_col,
                hist_forecast, future_forecast, forecast, last_date,
                horizon, period_type, forecast_color, forecast_opacity, show_confidence
            )

            # Display forecast table and statistics
            display_forecast_results(forecast, horizon, freq_str, hist_forecast, future_forecast)
    else:
        st.warning(f"⚠️ Need at least 3 data points for forecasting.")


def create_forecast_visualization(original_forecast_df, selected_date_col, selected_amount_col, 
                                hist_forecast, future_forecast, forecast, last_date,
                                horizon, period_type, forecast_color, forecast_opacity, show_confidence):
    """Create the forecast visualization chart."""
    fig_forecast = px.line(
        original_forecast_df, x=selected_date_col, y=selected_amount_col,
        labels={selected_date_col: "Date", selected_amount_col: "Actual Amount"},
        title=f"Forecast Analysis - Next {horizon} {period_type.title()}"
    )

    fig_forecast.update_traces(name="Historical Data", showlegend=True, line=dict(color="blue", dash="solid"))

    fig_forecast.add_scatter(
        x=hist_forecast["ds"], y=hist_forecast["yhat"],
        mode="lines", name="Prophet Fitted", line=dict(color="lightblue", dash="dot")
    )

    fig_forecast.add_scatter(
        x=future_forecast["ds"], y=future_forecast["yhat"],
        mode="lines", name="Forecast", line=dict(color="orange", dash="dash")
    )

    if show_confidence:
        fig_forecast.add_scatter(
            x=forecast["ds"], y=forecast["yhat_upper"],
            mode="lines", name="Upper Bound", line=dict(dash="dot", color="green"), showlegend=True
        )

        fig_forecast.add_scatter(
            x=forecast["ds"], y=forecast["yhat_lower"],
            mode="lines", name="Lower Bound", line=dict(dash="dot", color="red"), showlegend=True
        )

    fig_forecast.add_vrect(
        x0=last_date, x1=forecast["ds"].max(),
        fillcolor=forecast_color, opacity=forecast_opacity, line_width=0,
        annotation_text="Forecast Period", annotation_position="top left"
    )

    st.plotly_chart(fig_forecast, use_container_width=True)

    # Download option for chart
    png_bytes_forecast = export_plotly_fig(fig_forecast)
    if png_bytes_forecast:
        st.download_button(
            "⬇️ Download Forecast Chart (PNG)",
            data=png_bytes_forecast,
            file_name="forecast_chart.png",
            mime="image/png"
        )


def display_forecast_results(forecast, horizon, freq_str, hist_forecast, future_forecast):
    """Display forecast table and summary statistics."""
    # Prepare forecast table
    forecast_table = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon).copy()
    forecast_table.columns = ["Date", "Predicted", "Lower Bound", "Upper Bound"]

    if freq_str == "Y":
        forecast_table["Date"] = forecast_table["Date"].dt.strftime('%Y')
    else:
        forecast_table["Date"] = forecast_table["Date"].dt.strftime('%Y-%m-%d')

    forecast_table["Predicted"] = forecast_table["Predicted"].round(2)
    forecast_table["Lower Bound"] = forecast_table["Lower Bound"].round(2)
    forecast_table["Upper Bound"] = forecast_table["Upper Bound"].round(2)

    st.subheader("📅 Forecast Table (Future Predictions)")
    st.dataframe(forecast_table, use_container_width=True)

    # Download options
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download Forecast Data (CSV)",
            data=convert_df_to_csv(forecast_table),
            file_name="forecast_predictions.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            "⬇️ Download Forecast Data (Excel)",
            data=convert_df_to_excel(forecast_table),
            file_name="forecast_predictions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Summary statistics
    with st.expander("📊 Forecast Summary Statistics"):
        future_avg = future_forecast["yhat"].mean()
        historical_avg = hist_forecast["yhat"].mean()
        growth_rate = ((future_avg - historical_avg) / historical_avg) * 100 if historical_avg != 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Historical Average", f"{historical_avg:,.2f}")
        with col2:
            st.metric("Forecast Average", f"{future_avg:,.2f}")
        with col3:
            st.metric("Growth Rate", f"{growth_rate:.2f}%")