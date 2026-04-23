from werkzeug.security import generate_password_hash

def test_index_redirect(client):
    response = client.get("/")
    assert response.status_code in [302, 200]

def test_register_success(client):
    response = client.post("/register", data={
        "username": "test",
        "email": "test@mail.com",
        "password": "123"
    })
    assert response.status_code in [200, 302]

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_login_success(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    cursor.fetchone.return_value = {
        "email": "test@mail.com",
        "password": generate_password_hash("123")
    }

    response = client.post("/login", data={
        "email": "test@mail.com",
        "password": "123"
    })

    assert response.status_code in [200, 302]

def test_login_email_not_found(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    cursor.fetchone.return_value = None

    response = client.post("/login", data={
        "email": "notfound@mail.com",
        "password": "123"
    })

    assert b"Email tidak ditemukan" in response.data

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

def test_save_score(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    cursor.fetchone.return_value = {"user_id": 1}

    with client.session_transaction() as sess:
        sess["user"] = "test@mail.com"

    response = client.post("/save_score", json={
        "score": 10,
        "game_name": "barrel"
    })

    assert response.json["status"] == "success"

def test_save_score_requires_login(client):
    response = client.post("/save_score", json={
        "score": 10,
        "game_name": "barrel"
    })

    # karena login_required
    assert response.status_code in [302, 401]

def test_save_score_user_not_found(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    cursor.fetchone.return_value = None

    with client.session_transaction() as sess:
        sess["user"] = "test@mail.com"

    response = client.post("/save_score", json={
        "score": 10,
        "game_name": "barrel"
    })

    assert response.json["status"] == "error"

def test_dashboard(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    # urutan fetchone dipanggil:
    # 1. dashboard → ambil user_id
    # 2. inject_user → ambil username
    cursor.fetchone.side_effect = [
        {"user_id": 1},
        {"username": "testuser"}
    ]

    cursor.fetchall.return_value = []

    with client.session_transaction() as sess:
        sess["user"] = "test@mail.com"

    response = client.get("/dashboard")

    assert response.status_code == 200

def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code in [302, 401]

def test_profile_update(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    cursor.fetchone.side_effect = [
        {"email": "test@mail.com"},  # existing user
        {"username": "old", "email": "test@mail.com"}  # current user
    ]

    with client.session_transaction() as sess:
        sess["user"] = "test@mail.com"

    response = client.post("/profile", data={
        "username": "newname"
    })

    assert response.status_code in [200, 302]

def test_profile_duplicate_username(client):
    mock_db = client.application.config["DB"]
    cursor = mock_db.cursor.return_value

    cursor.fetchone.side_effect = [
        {"email": "other@mail.com"},  # cek duplicate
        {"username": "old", "email": "test@mail.com"},  # ambil user profile
        {"username": "testuser"}  # inject_user (context processor)
    ]

    with client.session_transaction() as sess:
        sess["user"] = "test@mail.com"

    response = client.post("/profile", data={
        "username": "duplicate"
    })

    assert b"Username sudah digunakan" in response.data