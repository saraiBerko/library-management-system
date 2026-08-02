def test_create_and_list_books(client):
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "isbn": "9780441013593"},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Dune"

    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_missing_book_returns_404(client):
    response = client.get("/books/999")
    assert response.status_code == 404
