import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config.settings import TCMB_API_KEY

class CustomSSLAdapter(HTTPAdapter):
    """
    Custom Adapter to handle legacy SSL/TLS settings for TCMB EVDS.
    Forces a lower security level to allow older ciphers.
    FIX: SSLV3_ALERT_HANDSHAKE_FAILURE
    """
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        context = create_urllib3_context(ciphers='DEFAULT@SECLEVEL=1')
        self.poolmanager = PoolManager(
            num_pools=connections, 
            maxsize=maxsize, 
            block=block, 
            ssl_context=context,
            **pool_kwargs
        )

class TCMBClient:
    BASE_URL = "https://evds2.tcmb.gov.tr/service/evds"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or TCMB_API_KEY
        self.session = requests.Session()
        self.session.mount('https://', CustomSSLAdapter())
    
    @st.cache_data(ttl=3600)
    def get_exchange_rates(_self, start_date: str, end_date: str, currencies: list = ["USD", "EUR"]) -> pd.DataFrame:
        """
        Fetch exchange rates from TCMB.
        Note: Using _self to exclude self from cache hashing.
        """
        if not _self.api_key:
            st.error("TCMB API Key is missing. Please set TCMB_API_KEY in .env file.")
            return pd.DataFrame()

        series_map = {
            "USD": "TP.DK.USD.A",
            "EUR": "TP.DK.EUR.A",
            "GBP": "TP.DK.GBP.A"
        }
        
        selected_series = [series_map[c] for c in currencies if c in series_map]
        series_str = "-".join(selected_series)
        
        params = {
            "series": series_str,
            "startDate": start_date,
            "endDate": end_date,
            "type": "json",
            "key": _self.api_key,
            "frequency": 1
        }
        
        params_no_key = {k: v for k, v in params.items() if k != "key"}
        query_string = "&".join([f"{k}={v}" for k, v in params_no_key.items()])
        url = f"{_self.BASE_URL}/{query_string}"
        
        headers = {
            "key": _self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = _self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "items" not in data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data["items"])
            
            if "Tarih" in df.columns:
                df["Date"] = pd.to_datetime(df["Tarih"], format="%d-%m-%Y")
            
            rename_dict = {}
            for k, v in series_map.items():
                api_key_name = v.replace(".", "_")
                if api_key_name in df.columns:
                    rename_dict[api_key_name] = k
            
            df.rename(columns=rename_dict, inplace=True)
            
            for col in currencies:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df.sort_values("Date") if "Date" in df.columns else df
            
        except Exception as e:
            st.error(f"Error fetching data from TCMB: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def get_cpi_data(_self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch CPI (Consumer Price Index) data from TCMB/TUIK and calculate rates.
        
        Series: 
        - TP.FG.J0: CPI (2003=100) General Index
        
        We calculate:
        - Inflation (YoY): (Index_t / Index_{t-12} - 1) * 100
        - Inflation (MoM): (Index_t / Index_{t-1} - 1) * 100
        """
        if not _self.api_key:
            return pd.DataFrame()

        series_map = {
            "CPI_Index": "TP.FG.J0"
        }
        
        series_str = "-".join(series_map.values())
        
        try:
            date_fmt = "%d-%m-%Y"
            s = datetime.strptime(start_date, date_fmt)
            s_prev = s - timedelta(days=550) 
            start_date_extended = s_prev.strftime(date_fmt)
        except:
            start_date_extended = start_date

        params = {
            "series": series_str,
            "startDate": start_date_extended,
            "endDate": end_date,
            "type": "json",
            "frequency": 5
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{_self.BASE_URL}/{query_string}"
        
        headers = {
            "key": _self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = _self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "items" not in data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data["items"])
            
            if "Tarih" in df.columns:
                df["Date"] = pd.to_datetime(df["Tarih"] + "-01", format="%Y-%m-%d", errors='coerce')
                if df["Date"].isna().any():
                     df["Date"] = pd.to_datetime(df["Tarih"], format="%d-%m-%Y", errors='coerce')

            rename_dict = {}
            for k, v in series_map.items():
                api_key_name = v.replace(".", "_")
                if api_key_name in df.columns:
                    rename_dict[api_key_name] = k
            
            df.rename(columns=rename_dict, inplace=True)
            
            if "CPI_Index" in df.columns:
                df["CPI_Index"] = pd.to_numeric(df["CPI_Index"], errors='coerce')
                
                df = df.sort_values("Date").reset_index(drop=True)
                
                df["CPI_Annual"] = df["CPI_Index"].pct_change(periods=12) * 100
                df["CPI_Monthly"] = df["CPI_Index"].pct_change(periods=1) * 100
            
            req_start = pd.to_datetime(start_date, format="%d-%m-%Y")
            df = df[df["Date"] >= req_start]

            return df
            
        except Exception as e:
            st.error(f"Error fetching CPI data: {str(e)}")
            return pd.DataFrame()
    @st.cache_data(ttl=3600)
    def get_interest_rates(_self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch Policy Rate / Weighted Average Funding Cost.
        
        Series:
        - TP.APIFON4: Weighted Average Funding Cost (Used as proxy for Policy Rate due to TP.PY.P01 restriction)
        """
        if not _self.api_key:
            return pd.DataFrame()

        series_map = {
            "Policy_Rate": "TP.APIFON4"
        }
        
        series_str = "-".join(series_map.values())
        
        params = {
            "series": series_str,
            "startDate": start_date,
            "endDate": end_date,
            "type": "json"
        }
        
        params_no_key = {k: v for k, v in params.items() if k != "key"}
        query_string = "&".join([f"{k}={v}" for k, v in params_no_key.items()])
        url = f"{_self.BASE_URL}/{query_string}"
        
        headers = {
            "key": _self.api_key,
            "User-Agent": "Mozilla/5.0"
        }
        
        try:
            response = _self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "items" not in data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data["items"])
            
            if "Tarih" in df.columns:
                df["Date"] = pd.to_datetime(df["Tarih"], format="%d-%m-%Y")
            
            rename_dict = {}
            for k, v in series_map.items():
                api_key_name = v.replace(".", "_")
                if api_key_name in df.columns:
                    rename_dict[api_key_name] = k
                    
            df.rename(columns=rename_dict, inplace=True)
            
            if "Policy_Rate" in df.columns:
                df["Policy_Rate"] = pd.to_numeric(df["Policy_Rate"], errors='coerce')
                
            df = df.dropna(subset=["Policy_Rate"])
            
            return df.sort_values("Date")
            
        except Exception as e:
            st.error(f"Error fetching Interest Rates: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def get_production_data(_self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch Real Sector / Production Data.
        
        Series:
        - TP.KKO.MA: Capacity Utilization Rate of Manufacturing Industry (Weighted Average)
        """
        if not _self.api_key:
            return pd.DataFrame()

        series_map = {
            "Capacity_Utilization": "TP.KKO.MA"
        }
        
        series_str = "-".join(series_map.values())
        
        params = {
            "series": series_str,
            "startDate": start_date,
            "endDate": end_date,
            "type": "json"
        }
        
        params_no_key = {k: v for k, v in params.items() if k != "key"}
        query_string = "&".join([f"{k}={v}" for k, v in params_no_key.items()])
        url = f"{_self.BASE_URL}/{query_string}"
        
        headers = {
            "key": _self.api_key,
            "User-Agent": "Mozilla/5.0"
        }
        
        try:
            response = _self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "items" not in data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data["items"])
            
            if "Tarih" in df.columns:
                df["Date"] = pd.to_datetime(df["Tarih"], format="%Y-%m")
            
            rename_dict = {}
            for k, v in series_map.items():
                api_key_name = v.replace(".", "_")
                if api_key_name in df.columns:
                    rename_dict[api_key_name] = k
                    
            df.rename(columns=rename_dict, inplace=True)
            
            if "Capacity_Utilization" in df.columns:
                df["Capacity_Utilization"] = pd.to_numeric(df["Capacity_Utilization"], errors='coerce')
                
            return df.sort_values("Date")
            
        except Exception as e:
            st.error(f"Error fetching Production Data: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def get_labor_data(_self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch Labor Market Data.
        
        Series:
        - TP.TIG08: Unemployment Rate (%)
        - TP.TIG07: Labor Force Participation Rate (%)
        """
        if not _self.api_key:
            return pd.DataFrame()

        series_map = {
            "Unemployment_Rate": "TP.TIG08",
            "Participation_Rate": "TP.TIG07"
        }
        
        series_str = "-".join(series_map.values())
        
        params = {
            "series": series_str,
            "startDate": start_date,
            "endDate": end_date,
            "type": "json"
        }
        
        params_no_key = {k: v for k, v in params.items() if k != "key"}
        query_string = "&".join([f"{k}={v}" for k, v in params_no_key.items()])
        url = f"{_self.BASE_URL}/{query_string}"
        
        headers = {
            "key": _self.api_key,
            "User-Agent": "Mozilla/5.0"
        }
        
        try:
            response = _self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "items" not in data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data["items"])
            
            if "Tarih" in df.columns:
                df["Date"] = pd.to_datetime(df["Tarih"], format="%Y-%m")
            
            rename_dict = {}
            for k, v in series_map.items():
                api_key_name = v.replace(".", "_")
                if api_key_name in df.columns:
                    rename_dict[api_key_name] = k
                    
            df.rename(columns=rename_dict, inplace=True)
            
            for col in ["Unemployment_Rate", "Participation_Rate"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
            return df.sort_values("Date")
            
        except Exception as e:
            st.error(f"Error fetching Labor Data: {e}")
            return pd.DataFrame()
