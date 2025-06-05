import requests
import streamlit as st
import pandas as pd

@st.cache_data(ttl=500)
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd,pln"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "usd": data["bitcoin"]["usd"],
            "pln": data["bitcoin"]["pln"]
        }
    except requests.RequestException:
        return {
            "usd": None,
            "pln": None
        }

@st.cache_data(ttl=600)
def get_btc_365day_prices(vs_currency="usd"):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": 365,
        "interval": "daily"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["Time"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df[["Time", "price"]]
    except Exception as e:
        st.error(f"Error fetching BTC prices for {vs_currency.upper()}: {e}")
        return None