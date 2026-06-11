import os
import json
from flask import Blueprint, jsonify, request, render_template, send_file
from werkzeug.utils import secure_filename
import requests as http_requests
from app.database import supabase

bp = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/books", methods=["GET"])
def get_books():
    result = supabase.table("books").select("*").order("created_at").execute()
    return jsonify(result.data)


@bp.route("/books/search", methods=["GET"])
def search_book():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Parâmetro q é obrigatório"}), 400

    try:
        res = http_requests.get(
            "https://openlibrary.org/search.json",
            params={"title": query, "limit": 15},
            timeout=5
        )
        res.raise_for_status()
        data = res.json()
    except http_requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Falha ao conectar com Open Library",
            "details": str(e)
        }), 502

    if not data.get("docs"):
        return jsonify({"error": "Livro não encontrado"}), 404

    results = []
    for doc in data["docs"]:
        cover_id = doc.get("cover_i")
        cover = (
            f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            if cover_id else ""
        )
        results.append({
            "title": doc.get("title", ""),
            "author": doc.get("author_name", [""])[0],
            "year": str(doc.get("first_publish_year", "")),
            "cover": cover
        })

    return jsonify(results)


@bp.route("/books", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    genre = request.form.get("genre")
    year = request.form.get("year")
    read_date = request.form.get("read_date")
    rating = request.form.get("rating")
    review = request.form.get("review")

    if not title:
        return jsonify({"error": "Título é obrigatório"}), 400

    cover_url = ""

    poster_url = request.form.get("poster_url")
    if poster_url:
        cover_url = poster_url

    file = request.files.get("image")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join("static/uploads", filename))
        cover_url = f"/static/uploads/{filename}"

    book = {
        "title": title,
        "author": author,
        "genre": genre,
        "year": year,
        "read_date": read_date,
        "rating": int(rating) if rating else 0,
        "review": review,
        "cover_url": cover_url
    }

    result = supabase.table("books").insert(book).execute()
    return jsonify({"success": True, "book": result.data[0]}), 201


@bp.route("/books/<string:book_id>", methods=["DELETE"])
def delete_book(book_id):
    result = supabase.table("books").delete().eq("id", book_id).execute()
    if not result.data:
        return jsonify({"error": "Livro não encontrado"}), 404
    return jsonify({"success": True, "removed": result.data[0]})


@bp.route("/books/export", methods=["GET"])
def export_books():
    result = supabase.table("books").select("*").execute()
    path = os.path.join(os.getcwd(), "books_export.json")
    with open(path, "w") as f:
        json.dump(result.data, f, ensure_ascii=False, indent=2)
    return send_file(path, as_attachment=True)


@bp.route("/books/import", methods=["POST"])
def import_books():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    data = json.load(file)
    supabase.table("books").insert(data).execute()
    return jsonify({"success": True, "count": len(data)})
