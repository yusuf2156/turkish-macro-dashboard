
import streamlit as st
import altair as alt
from datetime import datetime, timedelta
from data.fetchers.tcmb import TCMBClient
from components.cards import render_metric_card

def show_production():
    st.markdown("## 🏭 Production & Real Sector")
    st.markdown("Monitoring industrial activity and capacity utilization.")
    
    client = TCMBClient()
    
    # 5 Years of data for context
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5)
    
    start_str = start_date.strftime("%d-%m-%Y")
    end_str = end_date.strftime("%d-%m-%Y")
    
    with st.spinner("Fetching production data..."):
        df = client.get_production_data(start_str, end_str)
        
    if df.empty:
        st.error("No Production data available. Please check API connection.")
        return
        
    # --- Metrics ---
    latest = df.iloc[-1]
    
    # Capacity Utilization
    cap_curr = latest["Capacity_Utilization"]
    cap_prev = df.iloc[-2]["Capacity_Utilization"] if len(df) > 1 else cap_curr
    cap_delta = cap_curr - cap_prev
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        render_metric_card(
            "Capacity Utilization",
            f"{cap_curr:.1f}%",
            f"{cap_delta:+.1f}%",
            description="Manufacturing Industry"
        )
        st.info("The Capacity Utilization Rate (CUR) measures the extent to which the installed productive capacity is being used.")
        
    with col2:
        st.markdown("#### Historical Trend (5 Years)")
        chart = alt.Chart(df).mark_line(color="#2980B9").encode(
            x=alt.X('Date', title='Date', axis=alt.Axis(format='%Y')),
            y=alt.Y('Capacity_Utilization', title='Utilization Rate (%)', scale=alt.Scale(domain=[60, 90])),
            tooltip=[alt.Tooltip('Date', format='%Y-%m'), alt.Tooltip('Capacity_Utilization', format='.1f')]
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Data Table
    with st.expander("View Raw Data"):
        st.dataframe(df.sort_values("Date", ascending=False))
