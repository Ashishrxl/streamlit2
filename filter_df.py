import streamlit as st
import pandas as pd

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    st.markdown("---")
    with st.expander("Make filtered table", expanded=False):
    # Step 1: Let user pick the column for filtering
        item_column = st.selectbox("Select column to filter by:", df.columns)

    # Step 2: Create distinct list of items
        distinct_items = df[item_column].dropna().unique().tolist()

    # Step 3: User types a keyword for filtering items
        keyword = st.text_input(f"Search in '{item_column}':", "")

    # Step 4: Match keyword anywhere (case-insensitive)
        if keyword:
            suggestions = [item for item in distinct_items if keyword.lower() in str(item).lower()]
        else:
            suggestions = distinct_items

    # Step 5: Let user pick an item
        selected_item = st.selectbox("Select an Item:", suggestions)

    # Step 6: Let user choose which columns to display (no defaults)
        display_columns = st.multiselect(
            "Select columns to display:",
            options=df.columns
        )

    # Step 7: Filter DataFrame
        if display_columns:
            filtered_df = df[df[item_column] == selected_item][display_columns]
        else:
            filtered_df = pd.DataFrame()  # empty if no columns selected

    # Step 8: Show results
        st.write("### Filtered Data")
        st.dataframe(filtered_df)

    return filtered_df


