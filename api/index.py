from flask import Flask, Response, jsonify, request
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json

app = Flask(__name__)
BASE = 'https://lbkperp.lbank.com'


def proxy(path, params):
    url = BASE + path
    if params:
        url += '?' + urlencode({k: v for k, v in params.items() if v not in (None, '')})
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
        })
        with urlopen(req, timeout=12) as r:
            raw = r.read()
            status = r.status
        return Response(raw, status=status, content_type='application/json; charset=utf-8', headers={
            'Cache-Control': 'no-store',
            'Access-Control-Allow-Origin': '*',
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 502


@app.get('/api/instruments')
def instruments():
    return proxy('/cfd/openApi/v1/pub/instrument', {'productGroup': 'SwapU'})


@app.get('/api/markets')
def markets():
    return proxy('/cfd/openApi/v1/pub/marketData', {'productGroup': 'SwapU'})


@app.get('/api/depth')
def depth():
    return proxy('/cfd/openApi/v1/pub/marketOrder', {
        'depth': request.args.get('depth', '20'),
        'symbol': request.args.get('symbol', ''),
    })


@app.get('/api/kline')
def kline():
    return jsonify({
        'success': False,
        'error': 'LBank Futures K-line REST endpoint is not documented in the current public contract API.'
    }), 501
