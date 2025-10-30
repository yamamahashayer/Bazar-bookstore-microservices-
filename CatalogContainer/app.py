from flask import Flask, jsonify
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
