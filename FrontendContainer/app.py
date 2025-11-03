from flask import Flask, request
import requests

app = Flask(__name__)

CATALOG_URL = "http://catalog_service:5000"
ORDER_URL = "http://order_service:5001"

@app.get("/search/<query>")
def search(query):
    r = requests.get(f"{CATALOG_URL}/search/{query}")
    return r.text

@app.get("/info/<id>")
def info(id):
    r = requests.get(f"{CATALOG_URL}/info/{id}")
    return r.text

@app.post("/purchase/<id>")
def purchase(id):
    r = requests.post(f"{ORDER_URL}/purchase/{id}")
    return r.text

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
