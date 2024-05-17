import pytest

from analyse.analyse import calculate_month_on_month_growth, rank_websites_on_relative_total_visits_growth


@pytest.fixture
def init_db(db):
    db.create_table(
        table="website_total_visits",
        schema=[
            ("website", "TEXT"),
            ("snapshot_date", "TEXT"),
            ("total_visits", "INTEGER"),
        ],
        primary_key=["website", "snapshot_date"],
    )
    db.insert_records(
        table="website_total_visits",
        records=[
            ("example.com", "2024-01-01", 100),
            ("example.com", "2024-02-01", 100),
            ("example.com", "2024-03-01", 90),
            ("another.com", "2024-01-01", 200),
            ("another.com", "2024-02-01", 180),
            ("another.com", "2024-03-01", 90),
        ]
    )


def test_calculate_month_on_month_growth(db, init_db):
    # Call the function with the in-memory database connection
    result = calculate_month_on_month_growth(table="website_total_visits", column="total_visits", db=db)

    # Assert the result
    assert [
               ("another.com", "2024-02-01", 180, 200, -10.0),
               ("another.com", "2024-03-01", 90, 180, -50.0),
               ("example.com", "2024-02-01", 100, 100, 0.0),
               ("example.com", "2024-03-01", 90, 100, -10.0)
           ] == result


def test_rank_websites_on_relative_total_visits_growth(db, init_db):
    # Call the function with the in-memory database connection
    result = rank_websites_on_relative_total_visits_growth(db=db)

    # Assert the result
    assert [
               ('example.com', -10.0, 1),
               ('another.com', -55.0, 2),
           ] == result
