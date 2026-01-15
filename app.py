import streamlit as st
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT, COLORS
from data.fetchers.tcmb import TCMBClient
from components.cards import render_metric_card
from components.inflation import render_inflation_page
from components.interest import render_interest_page
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

with st.sidebar:
    st.title(f"{PAGE_ICON} Macro Dashboard")
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Go to",
        ["Overview", "Inflation", "Exchange Rates", "Interest Rates", "Production", "Labor Market", "About"]
    )
    
    st.markdown("---")
    st.markdown("### Settings")
    st.caption(f"v0.2.0 • Phase 2")

st.title(f"{PAGE_ICON} {PAGE_TITLE}")

if page == "Overview":
    from components.overview import show_overview
    show_overview()

elif page == "Inflation":
    render_inflation_page()

elif page == "Exchange Rates":
    st.write("### 💱 Exchange Rates (TCMB)")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
        
    if st.button("Fetch Data"):
        client = TCMBClient()
        start_str = start_date.strftime("%d-%m-%Y")
        end_str = end_date.strftime("%d-%m-%Y")
        
        with st.spinner("Fetching data from TCMB..."):
            df = client.get_exchange_rates(start_str, end_str)
            
        if not df.empty:
            st.success(f"Fetched {len(df)} records")
            
            df_chart = df.ffill()
            
            melted_df = df_chart.melt(id_vars=["Date"], value_vars=["USD", "EUR"], var_name="Currency", value_name="Rate")
            fig = px.line(melted_df, x="Date", y="Rate", color="Currency", title="USD & EUR / TRY Rates")
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("View Raw Data"):
                st.dataframe(df)
        else:
            st.warning("No data found or API key missing.")

elif page == "Interest Rates":
    render_interest_page()

elif page == "Production":
    import components.production as production
    production.show_production()

elif page == "Labor Market":
    import components.labor as labor
    labor.show_labor()

elif page == "About":
    st.markdown("### ℹ️ About Turkish Macroeconomic Dashboard")
    
    st.markdown("""
    **Turkish Macroeconomic Dashboard** is a real-time macroeconomic dashboard designed to track key indicators of the Turkish economy.
    
    #### 📡 Data Sources
    All data is sourced directly from the **Central Bank of the Republic of Turkey (TCMB) Electronic Data Delivery System (EVDS)**.
    - **API Endpoint**: `https://evds2.tcmb.gov.tr/service/evds/`
    - **Update Frequency**: Data is fetched in real-time upon user request.
    
    #### 🧮 Methodology & Notes
    - **Inflation**: Consumer Price Index (CPI) $(2003=100)$ is used. 
        - Annual Inflation (YoY) = $((Index_t / Index_{t-12}) - 1) * 100$
        - Monthly Inflation (MoM) = $((Index_t / Index_{t-1}) - 1) * 100$
    - **Interest Rates**: Due to API restrictions on the direct Policy Rate series (`TP.PY.P01`), we use the **Weighted Average Funding Cost** (`TP.APIFON4`) as a high-fidelity proxy. This rate closely tracks the official One-Week Repo Auction Rate.
    - **Exchange Rates**: Daily buying rates for USD and EUR are fetched from TCMB. Weekends and holidays are forward-filled for continuous visualization.
    - **Labor Market**: Data sourced from TCMB (via TÜİK) Household Labor Force Survey (Seasonally Adjusted).
    
    #### 🛠️ Tech Stack
    - **Framework**: Streamlit
    - **Data Processing**: Pandas, NumPy
    - **Visualization**: Altair, Plotly
    
    ---
    """)
    
    col_profile, col_text = st.columns([1, 4])
    with col_profile:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(current_dir, "assets", "profile_pic.jpg")
        st.image(img_path, width=120)
    with col_text:
        st.markdown("""
        **b. yusuf coban**  
        *Creator & Lead Developer*  
        v0.2.0
        """)
