import json
import os

BOOKS_FILE = "books_export.json"

def load_books():
    if os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_books(books):
    with open(BOOKS_FILE, "w") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

books = load_books()
