from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.fyers_service import (
    get_login_url,
    generate_access_token,
    get_profile,
    get_history,
    get_holdings,
    scan_stocks
)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend Running"}

@app.get("/login")
def login():

    return RedirectResponse(
        url=get_login_url()
    )

@app.get("/callback")
def callback(auth_code: str):

    token = generate_access_token(auth_code)

    return token

@app.get("/profile")
def profile(token: str):

    return get_profile(token)

@app.get("/holdings")
def holdings(token: str):

    return get_holdings(token)

@app.get("/history")
def history(symbol: str, token: str):

    return get_history(symbol, token)

@app.get("/scanner")
def scanner(token: str):

    return scan_stocks(token)

