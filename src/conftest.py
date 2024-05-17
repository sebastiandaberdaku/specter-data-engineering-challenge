import pytest

from database import Database


@pytest.fixture
def db():
    # Initialize Database with an in-memory database for testing
    db = Database(database_path=":memory:")
    yield db
    # Clean up: close database connection
    del db
