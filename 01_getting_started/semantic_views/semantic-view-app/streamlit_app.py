import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.title("📊 Sales Data Interactive Visualization")

session = get_active_session()

@st.cache_data
def load_data():
    query = """
    SELECT * FROM SEMANTIC_VIEW
    (
     SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM
        DIMENSIONS
                Item.Brand,
                Item.Category,
                Date.Year,
                Date.Month,
                Store.State
        METRICS
            StoreSales.TotalSalesQuantity
        WHERE
            Date.Year = '2002' AND Date.Month = '12' AND Item.Category = 'Books'
    )
    ORDER BY TotalSalesQuantity DESC
    """
    return session.sql(query).to_pandas()

df = load_data()

# Create selectbox for grouping option
group_by = st.selectbox(
    "Select grouping option:",
    options=['BRAND', 'STATE'],
    index=0
)

# Group the data based on selection
if group_by == 'BRAND':
    grouped_data = df.groupby('BRAND')['TOTALSALESQUANTITY'].sum().reset_index()
    grouped_data = grouped_data.set_index('BRAND')
    chart_title = "Total Sales Quantity by Brand"
else:  # group_by == 'STATE'
    grouped_data = df.groupby('STATE')['TOTALSALESQUANTITY'].sum().reset_index()
    grouped_data = grouped_data.set_index('STATE')
    chart_title = "Total Sales Quantity by State"

# Display the chart
st.subheader(chart_title)
st.bar_chart(grouped_data['TOTALSALESQUANTITY'])

# Optional: Display the data table
if st.checkbox("Show data table"):
    st.subheader("Grouped Data")
    st.dataframe(grouped_data)