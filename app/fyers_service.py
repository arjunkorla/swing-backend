import os
import requests
import hashlib
from dotenv import load_dotenv

import pandas as pd
from ta.momentum import RSIIndicator

load_dotenv()

FYERS_APP_ID = os.getenv("FYERS_APP_ID")
FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
FYERS_REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI")


def get_login_url():

    return (
        "https://api-t1.fyers.in/api/v3/generate-authcode?"
        f"client_id={FYERS_APP_ID}"
        f"&redirect_uri={FYERS_REDIRECT_URI}"
        "&response_type=code"
        "&state=sample"
        "&force_login=true"
    )


def generate_access_token(auth_code):

    app_id_hash = hashlib.sha256(
        f"{FYERS_APP_ID}:{FYERS_SECRET_KEY}".encode()
    ).hexdigest()

    payload = {
        "grant_type": "authorization_code",
        "appIdHash": app_id_hash,
        "code": auth_code
    }

    response = requests.post(
        "https://api-t1.fyers.in/api/v3/validate-authcode",
        json=payload
    )

    return response.json()


def get_profile(access_token):

    headers = {
        "Authorization": f"{FYERS_APP_ID}:{access_token}"
    }

    response = requests.get(
        "https://api-t1.fyers.in/api/v3/profile",
        headers=headers
    )

    return response.json()


def get_holdings(access_token):

    headers = {
        "Authorization": f"{FYERS_APP_ID}:{access_token}"
    }

    response = requests.get(
        "https://api-t1.fyers.in/api/v3/holdings",
        headers=headers
    )

    return response.json()


def get_history(symbol, access_token):

    headers = {
        "Authorization": f"{FYERS_APP_ID}:{access_token}"
    }

    url = (
        "https://api-t1.fyers.in/data/history?"
        f"symbol=NSE:{symbol}-EQ"
        "&resolution=D"
        "&date_format=1"
        "&range_from=2025-01-01"
        "&range_to=2026-05-05"
        "&cont_flag=1"
    )

    response = requests.get(
        url,
        headers=headers
    )

    return response.json()

def scan_stocks(access_token):

    symbols = [
        "RELIANCE",
        "INFY",
        "TCS",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "LT",
        "ITC",
        "BHARTIARTL",
        "AXISBANK"
    ]

    results = []

    for symbol in symbols:

        try:

            history = get_history(symbol, access_token)

            candles = history.get("candles", [])

            if not candles:
                continue

            df = pd.DataFrame(
                candles,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]
            )

            df["rsi"] = RSIIndicator(
                close=df["close"],
                window=14
            ).rsi()

            latest = df.iloc[-1]

            latest_close = latest["close"]
            latest_rsi = round(latest["rsi"], 2)

            score = 0

            if latest_rsi > 60:
                score += 40

            if latest_close > df["close"].mean():
                score += 30

            if latest["volume"] > df["volume"].mean():
                score += 30

            results.append({
                "symbol": symbol,
                "close": latest_close,
                "rsi": latest_rsi,
                "score": score
            })

        except Exception as e:

            results.append({
                "symbol": symbol,
                "error": str(e)
            })

    results = sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    return results