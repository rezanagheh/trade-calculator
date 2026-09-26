from flask import Flask, jsonify, request
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json

app = Flask(__name__)
BASE = "https://lbkperp.lbank.com"


def fetch(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urlencode(params)
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def unwrap(value):
    if isinstance(value, dict):
        for key in ("data", "list", "rows", "result"):
            if key in value:
                return unwrap(value[key])
    return value


@app.get("/api/markets")
def markets():
    try:
        data = fetch("/cfd/openApi/v1/pub/marketData", {"productGroup": "SwapU"})
        raw = unwrap(data)
        if not isinstance(raw, list):
            raw = []

        out = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("symbol") or item.get("symbolName") or "").upper()
            if not symbol:
                continue
            out.append({
                "symbol": symbol,
                "lastPrice": item.get("lastPrice") or item.get("price") or item.get("close"),
                "markedPrice": item.get("markedPrice"),
                "prePositionFeeRate": item.get("prePositionFeeRate"),
            })

        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e), "markets": []}), 502


@app.get("/api/instruments")
def instruments():
    try:
        data = fetch("/cfd/openApi/v1/pub/instrument", {"productGroup": "SwapU"})
        return jsonify(unwrap(data))
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.get("/api/depth")
def depth():
    try:
        params = {
            "depth": request.args.get("depth", "20"),
            "symbol": request.args.get("symbol", ""),
        }
        return jsonify(fetch("/cfd/openApi/v1/pub/marketOrder", params))
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.get("/api/kline")
def kline():
    return jsonify({
        "success": False,
        "error": "LBank Futures K-line REST endpoint is not documented in the current public contract API."
    }), 501
