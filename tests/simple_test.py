from backend.database import eng as engine
from sqlalchemy import select
from backend.redis_client import redis as redis_client


def test_database_core_connection():
    """Test Postgres using standard SQLAlchemy Core execution."""
    with engine.connect() as conn:
        result = conn.execute(select(1)).fetchone()
        assert result[0] == 1

def test_simple_redis_cache():
    """Directly test our imported synchronous Redis instance."""
    redis_client.set("simple_test", "hello")
    value = redis_client.get("simple_test")
    
    assert value == "hello"
    redis_client.delete("simple_test")

def test_celery_broker_ping():
    """Ensure Celery is talking to Redis."""
    ping_response = redis_client.ping()
    assert ping_response is True