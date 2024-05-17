import tempfile

import pytest

from database.database import Database


def test_create_table(db):
    # Define schema for test table
    schema = [("id", "INTEGER"), ("name", "TEXT")]

    # Call create_table method
    db.create_table(table="test_table1", schema=schema)

    # Retrieve column names from test table
    column_names = db._get_table_column_names(table="test_table1")

    # Assert that the created table has the expected columns
    assert "id" in column_names
    assert "name" in column_names


def test_insert_records(db):
    # Define schema for test table
    schema = [("id", "INTEGER"), ("name", "TEXT")]

    # Create test table
    db.create_table(table="test_table2", schema=schema)

    # Define records to insert
    records = [(1, "Alice"), (2, "Bob")]

    # Insert records into test table
    db.insert_records(table="test_table2", records=records)

    # Execute SQL query to retrieve inserted records
    result = db.execute_sql("SELECT * FROM test_table2;")

    # Assert that inserted records match the expected values
    assert result == records


def test_execute_sql(db):
    # Define schema for test table
    schema = [("id", "INTEGER"), ("name", "TEXT")]

    # Create test table
    db.create_table(table="test_table3", schema=schema)

    # Define records to insert
    records = [(1, "Alice"), (2, "Bob")]

    # Insert records into test table
    db.insert_records(table="test_table3", records=records)

    # Execute SQL query to retrieve records
    result = db.execute_sql("SELECT * FROM test_table3 WHERE id = 1;")

    # Assert that the result contains the expected record
    assert len(result) == 1
    assert result[0] == records[0]


@pytest.fixture(scope="function")
def database_file():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".db") as temp_file:
        yield temp_file.name


def test_singleton_database_instance(database_file):
    # Initialize two Database instances with the same database path
    db1 = Database(database_path=database_file)
    db2 = Database(database_path=database_file)

    # Assert that both instances refer to the same object
    assert db1 is db2

    # Check the connection object to ensure it's the same
    assert db1.connection is db2.connection
