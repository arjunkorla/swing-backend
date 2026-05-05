from fyers_apiv3.FyersWebsocket import data_ws

live_market_data = {}


def onmessage(message):

    symbol = message.get("symbol")

    if symbol:

        live_market_data[symbol] = {
            "ltp": message.get("ltp"),
            "volume": message.get("vol_traded_today"),
            "change": message.get("ch")
        }

        print(live_market_data[symbol])


def onerror(message):
    print("Error:", message)


def onclose(message):
    print("Connection closed:", message)


def onopen(ws):

    symbols = [
        "NSE:RELIANCE-EQ",
        "NSE:INFY-EQ",
        "NSE:TCS-EQ",
        "NSE:HDFCBANK-EQ",
        "NSE:SBIN-EQ"
    ]

    ws.subscribe(
        symbols=symbols,
        data_type="SymbolUpdate"
    )

    ws.keep_running()


def start_live_scanner(access_token):

    fyers = data_ws.FyersDataSocket(
        access_token=access_token,
        log_path="",
        litemode=False,
        write_to_file=False,
        reconnect=True,
        on_connect=onopen,
        on_close=onclose,
        on_error=onerror,
        on_message=onmessage
    )

    fyers.connect()