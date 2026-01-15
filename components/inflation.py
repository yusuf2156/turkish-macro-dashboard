import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data.fetchers.tcmb import TCMBClient
from datetime import datetime, timedelta

def render_inflation_page():
    st.header("INF 💰 Inflation Deep-Dive")
    st.markdown("Analysis of Consumer Price Index (CPI) trends using official TÜİK data via TCMB.")

    # Controls
    col1, col2 = st.columns(2)
    with col1:
        # Default to last 2 years for inflation
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=730))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    if st.button("Fetch Inflation Data"):
        client = TCMBClient()
        start_str = start_date.strftime("%d-%m-%Y")
        end_str = end_date.strftime("%d-%m-%Y")

        with st.spinner("Fetching inflation data..."):
            df = client.get_cpi_data(start_str, end_str)

        if not df.empty:
            st.success(f"Loaded {len(df)} months of data")
            
            # Latest Values
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            c1, c2 = st.columns(2)
            c1.metric("Annual Inflation (YoY)", f"{latest['CPI_Annual']:.2f}%", f"{latest['CPI_Annual'] - prev['CPI_Annual']:.2f}%", delta_color="inverse")
            c2.metric("Monthly Inflation (MoM)", f"{latest['CPI_Monthly']:.2f}%", f"{latest['CPI_Monthly'] - prev['CPI_Monthly']:.2f}%", delta_color="inverse")

            # Main Chart
            fig = go.Figure()
            
            # Annual Change Bar
            fig.add_trace(go.Bar(
                x=df['Date'],
                y=df['CPI_Annual'],
                name='Annual (YoY)',
                marker_color='#E30A17'
            ))
            
            # Monthly Change Line
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['CPI_Monthly'],
                name='Monthly (MoM)',
                yaxis='y2',
                line=dict(color='#1E3A5F', width=3)
            ))
            
            fig.update_layout(
                title="Consumer Price Index (CPI) Trends",
                yaxis=dict(title="Annual Change (%)"),
                yaxis2=dict(title="Monthly Change (%)", overlaying='y', side='right'),
                legend=dict(x=0, y=1.1, orientation='h'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("View Raw Data"):
                st.dataframe(df.sort_values("Date", ascending=False))
        
        else:
            st.warning("No data found. Check your API key and date range.")
