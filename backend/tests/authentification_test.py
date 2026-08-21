import pytest
from fastapi.testclient import TestClient
from api.main import app
from sqlalchemy import text
from services.authentification import verify_age
from datetime import datetime
Client = TestClient(app)

@pytest.mark.integration
def test_signup_with_correct_data(user_for_sign_up, db):
    response = Client.post("auth/signup",
                          json=user_for_sign_up) 
    assert response.status_code == 200

@pytest.mark.integration
def test_signup_with_pwd_not_strong(user_for_sign_up, db):
    user_for_sign_up["pwd_hash"] = "weak"
    response = Client.post("auth/signup", json=user_for_sign_up)
    assert response.status_code == 400 and response.json()["detail"] == "PASSWORD_NOT_STRONG"

@pytest.mark.integration
def test_signup_with_username_taken(user_for_sign_up, db):
    response = Client.post("auth/signup", json=user_for_sign_up)
    assert response.status_code == 200
    response2 = Client.post("auth/signup", json=user_for_sign_up)
    assert response2.status_code == 400 and response2.json()["detail"] == "USERNAME_TAKEN"

@pytest.mark.integration
def test_signup_with_email_taken(user_for_sign_up, db):
    response = Client.post("auth/signup", json=user_for_sign_up)
    assert response.status_code == 200
    user_for_sign_up["username"] = "U3_2"
    response2 = Client.post("auth/signup", json=user_for_sign_up)
    assert response2.status_code == 400 and response2.json()["detail"] == "EMAIL_TAKEN"

@pytest.mark.integration
def test_signup_with_underage_user(user_for_sign_up, db):
    user_for_sign_up["dob"] = "2010-05-21"
    response = Client.post("auth/signup", json=user_for_sign_up)
    assert response.status_code == 400 and response.json()["detail"] == "USER_UNDERAGE"

@pytest.mark.integration
def test_signin_with_correct_credentials(user_for_sign_up, db):
    response = Client.post("auth/signup", json=user_for_sign_up)
    assert response.status_code == 200
    credentials = {
        "email": user_for_sign_up["email"],
        "pwd": user_for_sign_up["pwd_hash"],
        "last_login": "2024-06-01T12:00:00"
    }
    response2 = Client.post("auth/signin", json=credentials)
    assert response2.status_code == 200
    assert "token" in response2.json()

@pytest.mark.integration
def test_signin_with_incorrect_credentials(user_for_sign_up, db):
    response = Client.post("auth/signup", json=user_for_sign_up)
    assert response.status_code == 200
    credentials = {
        "email": user_for_sign_up["email"],
        "pwd": "wrongpassword",
        "last_login": "2024-06-01T12:00:00"
    }
    response2 = Client.post("auth/signin", json=credentials)
    assert response2.status_code == 400 and response2.json()["detail"] == "INVALID_CREDENTIALS"

@pytest.mark.unit
@pytest.mark.parametrize("dob, expected", [
    (datetime.strptime("2000-01-01", "%Y-%m-%d").date(), True),
    (datetime.strptime("2010-01-01", "%Y-%m-%d").date(), False),
    (datetime.strptime("2020-01-01", "%Y-%m-%d").date(), False),
])
def test_verify_age(dob, expected):
    assert verify_age(dob) == expected