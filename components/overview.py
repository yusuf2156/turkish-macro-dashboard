import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from data.fetchers.tcmb import TCMBClient
from components.cards import render_metric_card

def calculate_delta(current, previous):
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def show_overview():
    st.markdown("## 🇹🇷 Executive Summary")
    st.markdown("Key economic indicators at a glance.")
    
    tcmb = TCMBClient()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=400)
    
    end_str = end_date.strftime("%d-%m-%Y")
    start_str = start_date.strftime("%d-%m-%Y")

    with st.spinner("Fetching latest economic data..."):
        try:
            df_cpi = tcmb.get_cpi_data(start_str, end_str)
            
            df_test_ex = tcmb.get_exchange_rates(start_str, end_str, currencies=["USD", "EUR"])
            
            df_int = tcmb.get_interest_rates(start_str, end_str)

            df_prod = tcmb.get_production_data(start_str, end_str)

            df_labor = tcmb.get_labor_data(start_str, end_date.strftime("%d-%m-%Y"))
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return

    chart_start_date = end_date - timedelta(days=365)
    
    st.markdown("### 🏷️ Inflation")
    col_inf_metric, col_inf_chart = st.columns([1, 3])
    
    with col_inf_metric:
        if not df_cpi.empty:
            latest_cpi = df_cpi.iloc[-1]
            current_yoy = latest_cpi['CPI_Annual']
            prev_yoy = df_cpi.iloc[-2]['CPI_Annual'] if len(df_cpi) > 1 else current_yoy
            delta_val = current_yoy - prev_yoy
            render_metric_card("Annual Inflation", f"{current_yoy:.2f}%", f"{delta_val:+.2f}%", "YoY Change")
        else:
            st.warning("No Data")

    with col_inf_chart:
        if not df_cpi.empty:
            df_cpi_chart = df_cpi[df_cpi['Date'] >= chart_start_date]
            chart_cpi = alt.Chart(df_cpi_chart).mark_line(point=True, color="#E30A17").encode(
                x=alt.X('Date', title='Date', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('CPI_Annual', title='Annual Inflation (%)', scale=alt.Scale(zero=False)),
                tooltip=[alt.Tooltip('Date', format='%d-%m-%Y'), alt.Tooltip('CPI_Annual', format='.2f')]
            ).properties(height=300)
            st.altair_chart(chart_cpi, use_container_width=True)

    st.divider()

    st.markdown("### 💱 Exchange Rates (USD/TRY)")
    col_fx_metric, col_fx_chart = st.columns([1, 3])
    
    with col_fx_metric:
        if not df_test_ex.empty:
            # Forward-fill and drop NaN to get valid latest values
            df_fx_valid = df_test_ex.ffill().dropna(subset=['USD'])
            if not df_fx_valid.empty:
                latest_ex = df_fx_valid.iloc[-1]
                current_usd = latest_ex['USD']
                prev_usd = df_fx_valid.iloc[-2]['USD'] if len(df_fx_valid) > 1 else current_usd
                delta_usd = current_usd - prev_usd
                render_metric_card("USD/TRY", f"{current_usd:.4f}", f"{delta_usd:+.4f}", "Daily Rate")
            else:
                st.warning("No Data")
        else:
            st.warning("No Data")

    with col_fx_chart:
        if not df_test_ex.empty:
            df_chart = df_test_ex.copy()
            df_chart = df_chart.ffill()
            
            df_chart = df_chart[df_chart['Date'] >= chart_start_date]
            
            base = alt.Chart(df_chart).encode(
                x=alt.X('Date', title='Date', axis=alt.Axis(format='%b %Y', grid=False))
            )
            
            area = base.mark_area(
                line={'color': '#1E3A5F'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1E3A5F', offset=0),
                           alt.GradientStop(color='rgba(30, 58, 95, 0.1)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                y=alt.Y('USD', title='USD/TRY', scale=alt.Scale(zero=False, padding=0.1), axis=alt.Axis(grid=True))
            )
            
            line = base.mark_line(color="#1E3A5F").encode(
                y=alt.Y('USD', scale=alt.Scale(zero=False))
            )
            
            chart_usd = (area + line).encode(
                tooltip=[alt.Tooltip('Date', format='%d-%m-%Y'), alt.Tooltip('USD', format='.4f')]
            ).properties(height=300)
            
            st.altair_chart(chart_usd, use_container_width=True)

    col_eur_metric, col_eur_chart = st.columns([1, 3])
    
    with col_eur_metric:
        if not df_test_ex.empty and 'EUR' in df_test_ex.columns:
            # Forward-fill and drop NaN to get valid latest values
            df_eur_valid = df_test_ex.ffill().dropna(subset=['EUR'])
            if not df_eur_valid.empty:
                latest_ex = df_eur_valid.iloc[-1]
                current_eur = latest_ex['EUR']
                prev_eur = df_eur_valid.iloc[-2]['EUR'] if len(df_eur_valid) > 1 else current_eur
                delta_eur = current_eur - prev_eur
                render_metric_card("EUR/TRY", f"{current_eur:.4f}", f"{delta_eur:+.4f}", "Daily Rate")
            else:
                st.warning("No Data")
    
    with col_eur_chart:
        if not df_test_ex.empty and 'EUR' in df_test_ex.columns:
            df_chart_eur = df_test_ex.copy()
            df_chart_eur = df_chart_eur.ffill()
            df_chart_eur = df_chart_eur[df_chart_eur['Date'] >= chart_start_date]
            
            base_eur = alt.Chart(df_chart_eur).encode(
                x=alt.X('Date', title='Date', axis=alt.Axis(format='%b %Y', grid=False))
            )

            area_eur = base_eur.mark_area(
                line={'color': '#1E3A5F'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1E3A5F', offset=0),
                           alt.GradientStop(color='rgba(30, 58, 95, 0.1)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                y=alt.Y('EUR', title='EUR/TRY', scale=alt.Scale(zero=False, padding=0.1), axis=alt.Axis(grid=True))
            )
            
            line_eur = base_eur.mark_line(color="#1E3A5F").encode(
                y=alt.Y('EUR', scale=alt.Scale(zero=False))
            )
            
            chart_eur = (area_eur + line_eur).encode(
                tooltip=[alt.Tooltip('Date', format='%d-%m-%Y'), alt.Tooltip('EUR', format='.4f')]
            ).properties(height=300)
            
            st.altair_chart(chart_eur, use_container_width=True)

    st.divider()

    st.markdown("### 🏦 Policy Rate")
    col_int_metric, col_int_chart = st.columns([1, 3])
    
    with col_int_metric:
        if not df_int.empty:
            latest_int = df_int.iloc[-1]
            current_rate = latest_int['Policy_Rate']
            prev_rate = current_rate
            for val in reversed(df_int['Policy_Rate'].values):
                if val != current_rate:
                    prev_rate = val
                    break
            delta_rate = current_rate - prev_rate
            render_metric_card("Policy Rate", f"{current_rate:.2f}%", f"{delta_rate:+.2f}%" if delta_rate != 0 else "0.00%", "1-Week Repo")
        else:
            st.warning("No Data")

    with col_int_chart:
        if not df_int.empty:
            df_int_chart = df_int[df_int['Date'] >= chart_start_date]
            chart_int = alt.Chart(df_int_chart).mark_line(color="#2ECC71", interpolate='step-after').encode(
                x=alt.X('Date', title='Date'),
                y=alt.Y('Policy_Rate', title='Policy Rate (%)', scale=alt.Scale(domain=[0, 60])),
                tooltip=[alt.Tooltip('Date', format='%d-%m-%Y'), alt.Tooltip('Policy_Rate', format='.2f')]
            ).properties(height=300)
            st.altair_chart(chart_int, use_container_width=True)
    
    st.divider()

    st.markdown("### 🏭 Production (Capacity Utilization)")
    col_prod_metric, col_prod_chart = st.columns([1, 3])

    with col_prod_metric:
        if 'df_prod' in locals() and not df_prod.empty:
            latest_prod = df_prod.iloc[-1]
            current_cap = latest_prod['Capacity_Utilization']
            prev_cap = df_prod.iloc[-2]['Capacity_Utilization'] if len(df_prod) > 1 else current_cap
            delta_cap = current_cap - prev_cap
            render_metric_card("Capacity Utilization", f"{current_cap:.1f}%", f"{delta_cap:+.1f}%", "Manufacturing")
        else:
            st.warning("No Data")

    with col_prod_chart:
        if 'df_prod' in locals() and not df_prod.empty:
            df_prod_chart = df_prod[df_prod['Date'] >= chart_start_date]
            chart_prod = alt.Chart(df_prod_chart).mark_line(point=True, color="#2980B9").encode(
                x=alt.X('Date', title='Date', axis=alt.Axis(format='%Y-%m')),
                y=alt.Y('Capacity_Utilization', title='Utilization Rate (%)', scale=alt.Scale(domain=[65, 85])),
                tooltip=[alt.Tooltip('Date', format='%Y-%m'), alt.Tooltip('Capacity_Utilization', format='.1f')]
            ).properties(height=300)
            
            st.altair_chart(chart_prod, use_container_width=True)
    
    st.divider()

    st.markdown("### 👷 Labor Market (Unemployment)")
    col_lab_metric, col_lab_chart = st.columns([1, 3])

    with col_lab_metric:
        if 'df_labor' in locals() and not df_labor.empty:
            latest_lab = df_labor.iloc[-1]
            current_unemp = latest_lab['Unemployment_Rate']
            prev_unemp = df_labor.iloc[-2]['Unemployment_Rate'] if len(df_labor) > 1 else current_unemp
            delta_unemp = current_unemp - prev_unemp
            render_metric_card("Unemployment Rate", f"{current_unemp:.1f}%", f"{delta_unemp:+.1f}%", "Seasonally Adj.")
        else:
            st.warning("No Data")

    with col_lab_chart:
        if 'df_labor' in locals() and not df_labor.empty:
            df_lab_chart = df_labor[df_labor['Date'] >= chart_start_date]
            chart_lab = alt.Chart(df_lab_chart).mark_line(point=True, color="#E74C3C").encode(
                x=alt.X('Date', title='Date', axis=alt.Axis(format='%Y-%m')),
                y=alt.Y('Unemployment_Rate', title='Unemployment Rate (%)', scale=alt.Scale(domain=[0, 15])),
                tooltip=[alt.Tooltip('Date', format='%Y-%m'), alt.Tooltip('Unemployment_Rate', format='.1f')]
            ).properties(height=300)
            st.altair_chart(chart_lab, use_container_width=True)
            
    st.divider()

    st.info("ℹ️ Charts display data for the last 1 year.")
