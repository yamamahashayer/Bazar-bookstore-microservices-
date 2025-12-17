from flask import Flask
import requests

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
    catalog = get_next_catalog()
    r = requests.get(f"{catalog}/search/{query}")
    return r.text

@app.get("/info/<int:id>")
def info(id):
    catalog = get_next_catalog()
    r = requests.get(f"{catalog}/info/{id}")
    return r.text

@app.post("/purchase/<int:id>")
def purchase(id):
    order = get_next_order()
    r = requests.post(f"{order}/purchase/{id}")
    return r.text

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
