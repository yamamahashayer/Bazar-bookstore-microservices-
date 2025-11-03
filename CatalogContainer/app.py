from flask import Flask, jsonify, request, abort
import csv, os

app = Flask(__name__)
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "books.csv")

def read_all():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_all(rows):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","title","topic","price","quantity"])
        w.writeheader(); w.writerows(rows)

def cast_row(r):
    return {
        "id": int(r["id"]),
        "title": r["title"],
        "topic": r["topic"],
        "price": float(r["price"]),
        "quantity": int(r["quantity"])
    }

@app.get("/search/<topic>")
def search(topic):
    items = [
        {"id": cast_row(r)["id"], "title": cast_row(r)["title"]}
        for r in read_all()
        if cast_row(r)["topic"] == topic
    ]
    return jsonify(items)

@app.get("/info/<int:item_id>")
def info(item_id):
    for r in read_all():
        if int(r["id"]) == item_id:
            c = cast_row(r)
            return jsonify({"title": c["title"], "quantity": c["quantity"], "price": c["price"]})
    abort(404)

@app.post("/update")
def update():
    data = request.get_json(force=True)
    item_id = int(data["id"])
    delta_qty = int(data.get("delta_qty", 0))
    new_price = data.get("new_price", None)

    rows = read_all()
    for i, r in enumerate(rows):
        if int(r["id"]) == item_id:
            q = int(r["quantity"]) + delta_qty
            if q < 0:
                abort(400, "quantity would be negative")
            r["quantity"] = str(q)
            if new_price is not None:
                r["price"] = str(float(new_price))
            rows[i] = r
            write_all(rows)
            return jsonify({"ok": True, "quantity": q, "price": float(r["price"])})

    abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
