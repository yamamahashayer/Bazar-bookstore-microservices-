# from flask import Flask
# import requests

# app = Flask(__name__)

# CATALOG_URLS = [
#     "http://catalog:5000",
#     "http://catalog_replica1:5001",
#     "http://catalog_replica2:5002"
# ]

# ORDER_URLS = [
#     "http://order:5003",
#     "http://order_replica1:5004",
#     "http://order_replica2:5005"
# ]


# catalog_index = 0
# order_index = 0

# def get_next_catalog():
#     global catalog_index
#     url = CATALOG_URLS[catalog_index]
#     catalog_index = (catalog_index + 1) % len(CATALOG_URLS)
#     return url

# def get_next_order():
#     global order_index
#     url = ORDER_URLS[order_index]
#     order_index = (order_index + 1) % len(ORDER_URLS)
#     return url

# @app.get("/search/<query>")
# def search(query):
#     catalog = get_next_catalog()
#     r = requests.get(f"{catalog}/search/{query}")
#     return r.text

# @app.get("/info/<int:id>")
# def info(id):
#     catalog = get_next_catalog()
#     r = requests.get(f"{catalog}/info/{id}")
#     return r.text

# @app.post("/purchase/<int:id>")
# def purchase(id):
#     order = get_next_order()
#     r = requests.post(f"{order}/purchase/{id}")
#     return r.text

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5006)



from flask import Flask, make_response, jsonify

import requests
import time

app = Flask(__name__)

CATALOG_URLS = [
    "http://catalog:5000",
    "http://catalog_replica1:5001",
    "http://catalog_replica2:5002"
]

ORDER_URLS = [
    "http://order:5003",
    "http://order_replica1:5004",
    "http://order_replica2:5005"
]

catalog_index = 0
order_index = 0

# ---------------------------
# Simple in-memory cache
# key -> {"value": <response_text>, "ts": <timestamp>}
# We cache only READ requests: search + info
# ---------------------------
CACHE = {}
CACHE_TTL_SECONDS = 0  # 0 means "no TTL" (never expire). You can set e.g. 30 if you want.

def cache_get(key: str):
    entry = CACHE.get(key)
    if not entry:
        return None

    if CACHE_TTL_SECONDS and (time.time() - entry["ts"] > CACHE_TTL_SECONDS):
        # expired
        del CACHE[key]
        return None

    return entry["value"]

def cache_set(key: str, value: str):
    CACHE[key] = {"value": value, "ts": time.time()}

def get_next_catalog():
    global catalog_index
    url = CATALOG_URLS[catalog_index]
    catalog_index = (catalog_index + 1) % len(CATALOG_URLS)
    return url

def get_next_order():
    global order_index
    url = ORDER_URLS[order_index]
    order_index = (order_index + 1) % len(ORDER_URLS)
    return url

@app.get("/search/<query>")
def search(query):
    cache_key = f"search:{query}"
    cached = cache_get(cache_key)

    if cached is not None:
        resp = make_response(cached, 200)
        resp.headers["X-Cache"] = "HIT"
        return resp

    catalog = get_next_catalog()
    r = requests.get(f"{catalog}/search/{query}")

    if r.status_code == 200:
        cache_set(cache_key, r.text)

    resp = make_response(r.text, r.status_code)
    resp.headers["X-Cache"] = "MISS"
    return resp


@app.get("/info/<int:id>")
def info(id):
    cache_key = f"info:{id}"
    cached = cache_get(cache_key)

    if cached is not None:
        resp = make_response(cached, 200)
        resp.headers["X-Cache"] = "HIT"
        return resp

    catalog = get_next_catalog()
    r = requests.get(f"{catalog}/info/{id}")

    if r.status_code == 200:
        cache_set(cache_key, r.text)

    resp = make_response(r.text, r.status_code)
    resp.headers["X-Cache"] = "MISS"
    return resp

@app.post("/purchase/<int:id>")
def purchase(id):
    # No caching for purchase (write)
    print(f"[FRONTEND] purchase request for item {id} -> forwarding to order")
    order = get_next_order()
    r = requests.post(f"{order}/purchase/{id}")
    return r.text, r.status_code


@app.post("/invalidate/<int:item_id>")
def invalidate(item_id):
    info_key = f"info:{item_id}"
    if info_key in CACHE:
        del CACHE[info_key]

    for k in list(CACHE.keys()):
        if k.startswith("search:"):
            del CACHE[k]

    print(f"[FRONTEND] invalidated cache for item {item_id}")
    return jsonify({"ok": True, "invalidated_item": item_id}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
