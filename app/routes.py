import os
import io
import json
import uuid
import zipfile
import requests as http_requests
from flask import Blueprint, jsonify, request, render_template, send_file
from app.database import supabase

bp = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_local_image(cover_url):
    return cover_url and os.environ.get("SUPABASE_URL", "") in cover_url


def get_storage_filename(cover_url):
    return cover_url.split("/covers/")[-1]


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
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        file_bytes = file.read()
        try:
            supabase.storage.from_("covers").upload(
                filename,
                file_bytes,
                {"content-type": file.content_type}
            )
            cover_url = supabase.storage.from_("covers").get_public_url(filename)
        except Exception as e:
            print(f"Erro no upload: {e}")
            cover_url = ""

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
    result = supabase.table("books").select("cover_url").eq("id", book_id).execute()
    if not result.data:
        return jsonify({"error": "Livro não encontrado"}), 404

    cover_url = result.data[0].get("cover_url", "")
    print(f"cover_url: {cover_url}")
    print(f"is_local: {is_local_image(cover_url)}")

    if is_local_image(cover_url):
        try:
            filename = get_storage_filename(cover_url)
            print(f"deletando: {filename}")
            supabase.storage.from_("covers").remove([filename])
            print("imagem deletada!")
        except Exception as e:
            print(f"Erro ao deletar imagem: {e}")

    result = supabase.table("books").delete().eq("id", book_id).execute()
    return jsonify({"success": True, "removed": result.data[0]})


@bp.route("/books/export", methods=["GET"])
def export_books():
    result = supabase.table("books").select("*").execute()
    books = result.data

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        images_map = {}
        for book in books:
            cover_url = book.get("cover_url", "")
            if is_local_image(cover_url):
                try:
                    img_res = http_requests.get(cover_url, timeout=10)
                    img_res.raise_for_status()
                    ext = cover_url.split(".")[-1]
                    img_filename = f"images/{book['id']}.{ext}"
                    zf.writestr(img_filename, img_res.content)
                    images_map[book["id"]] = img_filename
                except Exception as e:
                    print(f"Erro ao baixar imagem: {e}")

        for book in books:
            if book["id"] in images_map:
                book["cover_url"] = images_map[book["id"]]

        zf.writestr("books.json", json.dumps(books, ensure_ascii=False, indent=2))

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="bookshelf_export.zip"
    )


@bp.route("/books/import", methods=["POST"])
def import_books():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    filename = file.filename.lower()

    if filename.endswith(".zip"):
        with zipfile.ZipFile(file, "r") as zf:
            with zf.open("books.json") as jf:
                books = json.load(jf)

            for book in books:
                book.pop("id", None)
                book.pop("created_at", None)
                cover_path = book.get("cover_url", "")
                if cover_path.startswith("images/"):
                    try:
                        img_bytes = zf.read(cover_path)
                        ext = cover_path.split(".")[-1]
                        new_filename = f"{uuid.uuid4()}.{ext}"
                        supabase.storage.from_("covers").upload(
                            new_filename,
                            img_bytes,
                            {"content-type": f"image/{ext}"}
                        )
                        public_url = supabase.storage.from_(
                            "covers"
                        ).get_public_url(new_filename)
                        book["cover_url"] = public_url
                    except Exception as e:
                        print(f"Erro ao importar imagem: {e}")
                        book["cover_url"] = ""

    elif filename.endswith(".json"):
        books = json.load(file)
        for book in books:
            book.pop("id", None)
            book.pop("created_at", None)

    else:
        return jsonify({"error": "Formato inválido. Envie .zip ou .json"}), 400

    supabase.table("books").insert(books).execute()
    return jsonify({"success": True, "count": len(books)})
