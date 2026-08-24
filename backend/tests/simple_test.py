import pytest
from sqlalchemy import select
from backend.redis_client import redis

@pytest.mark.integration
def test_database_core_connection(db):
    with db.connect() as conn:
        result = conn.execute(select(1)).fetchone()
        assert result[0] == 1

@pytest.mark.integration
def test_simple_redis_cache():
    redis.set("simple_test", "pbc")
    value = redis.get("simple_test")
    
    assert value == "pbc"
    redis.delete("simple_test") 