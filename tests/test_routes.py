import pytest
from app import create_app
from unittest.mock import patch

@pytest.fixture(autouse=True)
def clear_books():
    from app import data_store
    data_store.books.clear()
    yield
    data_store.books.clear()

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_books_vazio(client):
    res = client.get("/books")
    assert res.status_code == 200
    assert res.get_json() == []

def test_add_book(client):
    res = client.post("/books", data={
        "title": "Dom Casmurro",
        "author": "Machado de Assis",
        "genre": "Romance",
        "year": "1899",
        "read_date": "2024-01-01",
        "rating": "8",
        "review": "Ótimo livro"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["book"]["title"] == "Dom Casmurro"

def test_delete_book(client):
    client.post("/books", data={
        "title": "Dom Casmurro",
        "author": "Machado de Assis",
        "genre": "Romance",
        "year": "1899",
        "read_date": "2024-01-01",
        "rating": "8",
        "review": "Ótimo livro"
    })
    res = client.delete("/books/0")
    assert res.status_code == 200

def test_delete_inexistente(client):
    res = client.delete("/books/99")
    assert res.status_code == 404

def test_add_book_com_imagem(client):
    import io
    import os
    os.makedirs("static/uploads", exist_ok=True)
    imagem_fake = (io.BytesIO(b"fake image content"), "capa.jpg")

    res = client.post("/books", data={
        "title": "1984",
        "author": "George Orwell",
        "genre": "Ficção Científica",
        "year": "1949",
        "read_date": "2024-02-01",
        "rating": "10",
        "review": "Clássico",
        "image": imagem_fake
    }, content_type="multipart/form-data")

    assert res.status_code == 201
    data = res.get_json()
    assert "capa.jpg" in data["book"]["cover_url"]

def test_exportar(client):
    client.post("/books", data={
        "title": "O Senhor dos Anéis",
        "author": "Tolkien",
        "genre": "Fantasia",
        "year": "1954",
        "read_date": "2024-03-01",
        "rating": "9",
        "review": "Incrível"
    })
    res = client.get("/books/export")
    assert res.status_code == 200
    assert res.content_type == "application/json"

def test_importar(client):
    import io
    import json

    livros = [{"title": "A Metamorfose", "author": "Kafka", "genre": "Drama",
               "year": "1915", "read_date": "2024-04-01",
               "rating": 9, "review": "Obra prima", "cover_url": ""}]

    arquivo = (io.BytesIO(json.dumps(livros).encode()), "livros.json")

    res = client.post("/books/import", data={"file": arquivo},
                      content_type="multipart/form-data")

    assert res.status_code == 200
    assert res.get_json()["count"] == 1

def test_add_book_sem_titulo(client):
    res = client.post("/books", data={
        "title": "",
        "author": "Autor",
        "genre": "Romance",
        "year": "2020",
        "read_date": "2024-01-01",
        "rating": "8",
        "review": ""
    })
    assert res.status_code == 400

def test_add_book_rating_zero(client):
    res = client.post("/books", data={
        "title": "Livro Sem Nota",
        "author": "Autor",
        "genre": "Drama",
        "year": "2020",
        "read_date": "2024-01-01",
        "rating": "0",
        "review": ""
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["book"]["rating"] == 0

def test_add_book_rating_maximo(client):
    res = client.post("/books", data={
        "title": "Livro Perfeito",
        "author": "Autor",
        "genre": "Ação",
        "year": "2024",
        "read_date": "2024-12-31",
        "rating": "10",
        "review": "Incrível"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["book"]["rating"] == 10

def test_add_book_sem_review(client):
    res = client.post("/books", data={
        "title": "Livro Sem Review",
        "author": "Autor",
        "genre": "Comédia",
        "year": "2022",
        "read_date": "2024-06-01",
        "rating": "5",
        "review": ""
    })
    assert res.status_code == 201

def test_delete_primeiro_de_varios(client):
    client.post("/books", data={"title": "Livro A", "author": "Autor A",
        "genre": "Ação", "year": "2020", "read_date": "2024-01-01",
        "rating": "5", "review": ""})
    client.post("/books", data={"title": "Livro B", "author": "Autor B",
        "genre": "Drama", "year": "2021", "read_date": "2024-02-01",
        "rating": "7", "review": ""})

    res = client.delete("/books/0")
    assert res.status_code == 200

    res = client.get("/books")
    livros = res.get_json()
    assert livros[0]["title"] == "Livro B"

def test_search_openlibrary_sucesso(client):
    mock_response = {
        "docs": [{
            "title": "Dom Casmurro",
            "author_name": ["Machado de Assis"],
            "first_publish_year": 1899,
            "cover_i": 12345
        }]
    }
    with patch("app.routes.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = mock_response

        res = client.get("/books/search?q=Dom+Casmurro")
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)
        assert data[0]["title"] == "Dom Casmurro"
        assert data[0]["author"] == "Machado de Assis"
        assert data[0]["year"] == "1899"

def test_search_openlibrary_nao_encontrado(client):
    mock_response = {"docs": []}
    with patch("app.routes.requests.get") as mock_get:
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = mock_response

        res = client.get("/books/search?q=xyzlivroinexistente")
        assert res.status_code == 404

def test_search_openlibrary_sem_parametro(client):
    res = client.get("/books/search")
    assert res.status_code == 400