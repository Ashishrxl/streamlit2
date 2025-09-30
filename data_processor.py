"""
Data processing and table generation functionality.
"""

import pandas as pd
import streamlit as st
from utils import find_col_ci, convert_df_to_csv, convert_df_to_excel, toggle_state
from pdf_download import pdfapp

def process_alldata_tables(uploaded_df):
    """Process uploaded CSV into normalized tables for alldata.csv structure."""
    # Extract individual tables
    id_col = find_col_ci(uploaded_df, "ID")
    name_col = find_col_ci(uploaded_df, "Name")
    party_df = uploaded_df[[id_col, name_col]].drop_duplicates().reset_index(drop=True) if id_col and name_col else pd.DataFrame()

    bill_col = find_col_ci(uploaded_df, "Bill")
    partyid_col = find_col_ci(uploaded_df, "PartyId")
    date_col_master = find_col_ci(uploaded_df, "Date")
    amount_col_master = find_col_ci(uploaded_df, "Amount")
    bill_df = (
        uploaded_df[[bill_col, partyid_col, date_col_master, amount_col_master]].drop_duplicates().reset_index(drop=True)
        if bill_col and partyid_col and date_col_master and amount_col_master else pd.DataFrame()
    )

    billdetails_cols = [find_col_ci(uploaded_df, c) for c in ["IndexId", "Billindex", "Item", "Qty", "Rate", "Less"]]
    billdetails_cols = [c for c in billdetails_cols if c]
    billdetails_df = uploaded_df[billdetails_cols].drop_duplicates().reset_index(drop=True) if billdetails_cols else pd.DataFrame()

    # Create joined tables
    try:
        party_bill_df = pd.merge(
            party_df, bill_df, left_on=id_col, right_on=partyid_col, how="inner", suffixes=("_party", "_bill")
        ) if not party_df.empty and not bill_df.empty else pd.DataFrame()
    except Exception:
        party_bill_df = pd.DataFrame()

    try:
        billindex_col = find_col_ci(uploaded_df, "Billindex")
        bill_billdetails_df = pd.merge(
            bill_df, billdetails_df, left_on=bill_col, right_on=billindex_col, how="inner", suffixes=("_bill", "_details")
        ) if not bill_df.empty and not billdetails_df.empty else pd.DataFrame()
    except Exception:
        bill_billdetails_df = pd.DataFrame()

    tables_dict = {
        "Uploaded Table": uploaded_df,
        "Party": party_df,
        "Bill": bill_df,
        "BillDetails": billdetails_df,
        "Party + Bill": party_bill_df,
        "Bill + BillDetails": bill_billdetails_df
    }
    
    return tables_dict


def process_regular_tables(uploaded_df):
    """Process uploaded CSV as single table."""
    return {"Uploaded Table": uploaded_df}


def display_tables_preview(tables_dict):
    """Display expandable preview of all tables."""
    st.subheader("🗂️ Tables Preview")
    
    for table_name, table_df in tables_dict.items():
        state_key = f"expand_{table_name.replace(' ', '')}"
        if state_key not in st.session_state:
            st.session_state[state_key] = False

        btn_label = f"Minimise {table_name} Table" if st.session_state[state_key] else f"Expand {table_name} Table"
        st.button(btn_label, key=f"btn{table_name}", on_click=toggle_state, args=(state_key,))

        if st.session_state[state_key]:
            st.write(f"### {table_name} Table (First 20 Rows)")
            if not table_df.empty:
                st.dataframe(table_df.head(20))
                
                with st.expander(f"📖 Show full {table_name} Table"):
                    st.markdown("", unsafe_allow_html=True)
                    st.dataframe(table_df)
                    st.download_button(
                        f"⬇️ Download {table_name} (PDF)",
                        data=pdfapp(table_df),
                        file_name=f"{table_name.lower().replace(' ', '')}.pdf",
                        mime="application/pdf",
                    )   
                    st.download_button(
                        f"⬇️ Download {table_name} (CSV)",
                        data=convert_df_to_csv(table_df),
                        file_name=f"{table_name.lower().replace(' ', '')}.csv",
                        mime="text/csv",
                    )
                
                    st.download_button(
                        f"⬇️ Download {table_name} (Excel)",
                        data=convert_df_to_excel(table_df),
                        file_name=f"{table_name.lower().replace(' ', '')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            else:
                st.info("ℹ️ Not available from the uploaded CSV.")


def aggregate_data_by_time(selected_df, date_col_sel, time_period, grouping_choice, name_col_sel, categorical_cols, numerical_cols):
    """Aggregate data by time period and grouping options."""
    try:
        selected_df[date_col_sel] = pd.to_datetime(selected_df[date_col_sel], errors="coerce")
        selected_df = selected_df.sort_values(by=date_col_sel).reset_index(drop=True)
        selected_df['Year_Month'] = selected_df[date_col_sel].dt.to_period('M')
        selected_df['Year'] = selected_df[date_col_sel].dt.to_period('Y')
        
        period_col = 'Year_Month' if time_period == "Monthly" else 'Year'
        
        if grouping_choice == "Group by Name" and name_col_sel:
            grouped_df = selected_df.groupby([period_col, name_col_sel], as_index=False)[numerical_cols].sum()
            grouped_df[period_col] = grouped_df[period_col].astype(str)
            selected_df = grouped_df.copy()
            date_col_sel = period_col
            st.success(f"✅ Data aggregated {time_period.lower()} and grouped by {name_col_sel} with numerical values summed.")
            
        elif grouping_choice == "Group by Custom Columns":
            st.markdown(f"#### Select Columns for {time_period} Grouping")
            selected_group_cols = st.multiselect(
                f"Choose columns to group by (in addition to {time_period.lower()} grouping):",
                categorical_cols,
                default=[],
                help=f"Select one or more columns to group your data by within each {time_period.lower()} period. Numerical columns will be summed."
            )
            
            if selected_group_cols:
                group_by_cols = [period_col] + selected_group_cols
                grouped_df = selected_df.groupby(group_by_cols, as_index=False)[numerical_cols].sum()
                grouped_df[period_col] = grouped_df[period_col].astype(str)
                selected_df = grouped_df.copy()
                date_col_sel = period_col
                st.success(f"✅ Data aggregated {time_period.lower()} and grouped by {', '.join(selected_group_cols)} with numerical values summed.")
            else:
                grouped_df = selected_df.groupby(period_col, as_index=False)[numerical_cols].sum()
                grouped_df[period_col] = grouped_df[period_col].astype(str)
                selected_df = grouped_df.copy()
                date_col_sel = period_col
                st.info(f"ℹ️ No grouping columns selected. Data aggregated {time_period.lower()} only.")
                
        elif grouping_choice == "No Grouping":
            grouped_df = selected_df.groupby(period_col, as_index=False)[numerical_cols].sum()
            grouped_df[period_col] = grouped_df[period_col].astype(str)
            selected_df = grouped_df.copy()
            date_col_sel = period_col
            st.success(f"✅ Data aggregated {time_period.lower()} only. All numerical values summed per {time_period.lower()} period.")
            
        return selected_df, date_col_sel
        
    except Exception as e:
        st.warning(f"⚠️ Could not process date grouping: {e}")
        st.error(f"Error details: {str(e)}")
        return selected_df, date_col_sel
