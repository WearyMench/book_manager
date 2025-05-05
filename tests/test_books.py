import json

def test_get_books(client):
    response = client.get('/books')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data

def test_create_book(client):
    book_data = {
        "title": "New Test Book",
        "author": "New Test Author",
        "published_date": "2024-02-01",
        "summary": "New Test Summary"
    }
    response = client.post(
        '/books',
        data=json.dumps(book_data),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert data["data"]["title"] == book_data["title"]
    assert data["data"]["author"] == book_data["author"]

def test_update_book(client, sample_book):
    update_data = {
        "title": "Updated Book",
        "author": "Updated Author"
    }
    response = client.put(
        f'/books/{sample_book.id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert data["data"]["title"] == update_data["title"]
    assert data["data"]["author"] == update_data["author"]

def test_delete_book(client, sample_book):
    response = client.delete(f'/books/{sample_book.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    
    # Verify book is deleted
    response = client.get(f'/books/{sample_book.id}')
    assert response.status_code == 404

def test_create_book_invalid_data(client):
    book_data = {
        "title": "",  # Invalid empty title
        "author": "Test Author"
    }
    response = client.post(
        '/books',
        data=json.dumps(book_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data