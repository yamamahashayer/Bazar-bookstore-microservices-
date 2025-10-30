from flask import Flask
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
