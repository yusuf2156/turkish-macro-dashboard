
import streamlit as st
import altair as alt
from datetime import datetime, timedelta
from data.fetchers.tcmb import TCMBClient
from components.cards import render_metric_card

def show_labor():
    st.markdown("## 👷 Labor Market")
    st.markdown("Unemployment and labor force participation indicators.")
    
    client = TCMBClient()
    
    # 5 Years of data for context
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5)
    
    start_str = start_date.strftime("%d-%m-%Y")
    end_str = end_date.strftime("%d-%m-%Y")
    
    with st.spinner("Fetching labor market data..."):
        df = client.get_labor_data(start_str, end_str)
        
    if df.empty:
        st.error("No Labor Market data available. Please check API connection.")
        return
        
    # --- Metrics ---
    latest = df.iloc[-1]
    
    # Unemployment
    unemp_curr = latest["Unemployment_Rate"]
    unemp_prev = df.iloc[-2]["Unemployment_Rate"] if len(df) > 1 else unemp_curr
    unemp_delta = unemp_curr - unemp_prev
    
    # Participation
    part_curr = latest["Participation_Rate"]
    part_prev = df.iloc[-2]["Participation_Rate"] if len(df) > 1 else part_curr
    part_delta = part_curr - part_prev
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_metric_card(
            "Unemployment Rate",
            f"{unemp_curr:.1f}%",
            f"{unemp_delta:+.1f}%",
            description="Seasonally Adjusted"
        )
        
    with col2:
         render_metric_card(
            "Participation Rate",
            f"{part_curr:.1f}%",
            f"{part_delta:+.1f}%",
            description="Labor Force Participation"
        )
        
    st.divider()
    
    # --- Charts ---
    st.markdown("#### Historical Trends (5 Years)")
    
    # Dual Chart? Or separate? Let's do separate for clarity vertically, or dual axis.
    # Separate is cleaner.
    
    tab1, tab2 = st.tabs(["Unemployment Rate", "Participation Rate"])
    
    with tab1:
        chart_unemp = alt.Chart(df).mark_line(color="#E74C3C").encode(
            x=alt.X('Date', title='Date', axis=alt.Axis(format='%Y')),
            y=alt.Y('Unemployment_Rate', title='Unemployment Rate (%)', scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('Date', format='%Y-%m'), alt.Tooltip('Unemployment_Rate', format='.1f')]
        ).properties(height=350)
        st.altair_chart(chart_unemp, use_container_width=True)
        
    with tab2:
        chart_part = alt.Chart(df).mark_line(color="#2ECC71").encode(
            x=alt.X('Date', title='Date', axis=alt.Axis(format='%Y')),
            y=alt.Y('Participation_Rate', title='Participation Rate (%)', scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('Date', format='%Y-%m'), alt.Tooltip('Participation_Rate', format='.1f')]
        ).properties(height=350)
        st.altair_chart(chart_part, use_container_width=True)

    # Data Table
    with st.expander("View Raw Data"):
            st.dataframe(df.sort_values("Date", ascending=False))
