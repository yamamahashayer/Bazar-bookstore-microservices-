from flask import Flask, jsonify, abort
import csv, os, uuid, requests

CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog:5001")
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "orders.csv")
app = Flask(__name__)

def append_order(item_id, title):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","item_id","title"])
        if f.tell() == 0:
            w.writeheader()
        w.writerow({"id": str(uuid.uuid4()), "item_id": item_id, "title": title})

@app.post("/purchase/<int:item_id>")
def purchase(item_id):
    r = requests.get(f"{CATALOG_URL}/info/{item_id}")
    if r.status_code != 200:
        abort(404, "item not found")
    info = r.json()
    if info["quantity"] <= 0:
        abort(400, "out of stock")

    upd = requests.post(f"{CATALOG_URL}/update", json={"id": item_id, "delta_qty": -1})
    if upd.status_code != 200:
        abort(upd.status_code, upd.text)

    append_order(item_id, info["title"])
    return jsonify({"ok": True, "message": f"bought book {info['title']}"})

@app.get("/")
def home():
    return jsonify({"routes": ["POST /purchase/<id>"], "catalog": CATALOG_URL})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
