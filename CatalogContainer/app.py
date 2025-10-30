from flask import Flask
import csv, os

app = Flask(__name__)
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "books.csv")

def read_all():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
