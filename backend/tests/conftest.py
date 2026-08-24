import pytest
from database import eng, metadata, init_db
from sqlalchemy import text

@pytest.fixture(scope="session", autouse=True)
def init():
    with eng.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    metadata.create_all(eng)
    yield
    metadata.drop_all(eng)
        
@pytest.fixture(autouse=True)
def setup_and_teardown():
    with eng.begin() as conn:
            conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
    yield
    with eng.begin() as conn:
        conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        
@pytest.fixture
def db():
    return eng

@pytest.fixture
def user_for_sign_up():
    return {
        "username": "U3",
        "email": "U3@egmail.com",
        "phone": "+212621212122",
        "gender": "male",
        "pwd_hash": "strongpwd123@",
        "name": "U3",
        "dob": "2006-05-21",
        "country": "MA"
        
    }
    
    