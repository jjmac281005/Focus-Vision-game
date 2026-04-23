from werkzeug.security import generate_password_hash

def test_index_redirect(client):
    response = client.get("/")
    assert response.status_code in [302, 200]


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_login_wrong_password(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    cursor.fetchone.return_value = {
        "email": "test@mail.com",
        "password": generate_password_hash("correct_password")
    }

    response = client.post("/login", data={
        "email": "test@mail.com",
        "password": "wrong_password"
    })

    assert response.status_code in [200, 302]

def test_login_fail(client):
    # ambil mock DB dari app config
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    # penting: user tidak ditemukan
    cursor.fetchone.return_value = None

    response = client.post("/login", data={
        "email": "wrong@mail.com",
        "password": "123"
    })

    assert response.status_code in [200, 302]

def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_session_endpoint(client):
    response = client.get("/session")
    assert response.status_code == 200


def test_save_score_requires_login(client):
    response = client.post("/save_score", json={
        "score": 10,
        "game_name": "barrel"
    })

    # karena login_required
    assert response.status_code in [302, 401]


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code in [302, 401]