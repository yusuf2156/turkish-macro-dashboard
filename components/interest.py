import streamlit as st
import plotly.graph_objects as go
from data.fetchers.tcmb import TCMBClient
from datetime import datetime, timedelta

def render_interest_page():
    st.header("INT 📈 Interest Rates & Monetary Policy")
    st.markdown("Tracking the Central Bank of the Republic of Turkey (TCMB) Policy Rate (One-Week Repo Auction Rate).")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=730))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    if st.button("Fetch Interest Rates"):
        client = TCMBClient()
        start_str = start_date.strftime("%d-%m-%Y")
        end_str = end_date.strftime("%d-%m-%Y")

        with st.spinner("Fetching policy rate data..."):
            df = client.get_interest_rates(start_str, end_str)

        if not df.empty:
            st.success(f"Loaded policy rate history")
            
            latest = df.iloc[-1]
            
            current_rate = latest['Policy_Rate']
            
            prev_rate = current_rate
            for rate in df['Policy_Rate'].iloc[::-1]:
                 if rate != current_rate:
                     prev_rate = rate
                     break
            
            delta = current_rate - prev_rate
            
            c1, c2 = st.columns(2)
            c1.metric("Policy Rate", f"{current_rate:.2f}%", f"{delta:.2f}%", delta_color="inverse")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Policy_Rate'],
                mode='lines',
                name='Policy Rate',
                line=dict(color='#1E3A5F', width=3, shape='hv')
            ))
            
            fig.update_layout(
                title="TCMB One-Week Repo Auction Rate",
                yaxis=dict(title="Rate (%)"),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("View Raw Data"):
                st.dataframe(df.sort_values("Date", ascending=False))
        
        else:
            st.warning("No data found. Check your API key and date range.")
