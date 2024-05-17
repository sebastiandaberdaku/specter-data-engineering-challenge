from datetime import datetime
from unittest.mock import Mock

import pytest

from transform.scrape import Scrape


@pytest.fixture
def mock_database():
    return Mock()


@pytest.fixture
def scrape(mock_database):
    domain = "example.com"
    snapshot_date = "2024-05-20T00:00:00+00:00"
    global_rank = "100"
    total_visits = "10000"
    bounce_rate = "30%"
    pages_per_visit = "2.5"
    avg_visit_duration = "00:05:30"
    one_month_rank_change = "5"
    two_month_rank_change = "-3"
    visits_history = '{"2024-04-01": 5000, "2024-04-02": 5500}'
    last_month_change_in_traffic = "10.5"
    top_countries = """[
        {
            "countryAlpha2Code": "US", 
            "countryUrlCode": "united-states", 
            "visitsShare": 0.39795546411196864, 
            "visitsShareChange": -0.13638365185049084
        }, 
        {
            "countryAlpha2Code": "IN", 
            "countryUrlCode": "india", 
            "visitsShare": 0.09417928366707747, 
            "visitsShareChange": -0.110635968890194
        }
    ]"""
    age_distribution = """[
        {   
            "minAge": 18, 
            "maxAge": 34, 
            "value": 0.25
        }, 
        {   "minAge": 35, 
            "maxAge": 54, 
            "value": 0.25
        }, 
        {   
            "minAge": 55, 
            "value": 0.5
        }
    ]"""

    return Scrape(
        domain=domain,
        snapshot_date=snapshot_date,
        global_rank=global_rank,
        total_visits=total_visits,
        bounce_rate=bounce_rate,
        pages_per_visit=pages_per_visit,
        avg_visit_duration=avg_visit_duration,
        one_month_rank_change=one_month_rank_change,
        two_month_rank_change=two_month_rank_change,
        visits_history=visits_history,
        last_month_change_in_traffic=last_month_change_in_traffic,
        top_countries=top_countries,
        age_distribution=age_distribution,
        db=mock_database,
    )


def test_scrape_init(scrape):
    assert scrape.snapshot_date == datetime.fromisoformat("2024-05-20").date()  # Converted from timestamp
    assert scrape.global_rank == 100  # global rank converted to int
    assert scrape.total_visits == 10000  # Total visits converted to int
    assert scrape.bounce_rate == 0.30  # Bounce rate converted to float
    assert scrape.pages_per_visit == 2.5  # Pages per visit converted to float
    assert scrape.avg_visit_duration == 330  # Avg visit duration converted to int seconds
    assert scrape.one_month_rank_change == 5  # One-month rank change converted to int
    assert scrape.two_month_rank_change == -3  # Two-month rank change converted to int
    assert scrape.visits_history == {"2024-04-01": 5000, "2024-04-02": 5500}  # Visits history converted to dict
    assert scrape.last_month_change_in_traffic == 10.5  # Last month change in traffic converted to float
    assert scrape.top_countries == ["US", "IN"]  # Top countries converted to list
    assert scrape.age_distribution == {
        "18 - 34": 0.25,
        "35 - 54": 0.25,
        "55+": 0.5
    }  # Age distribution converted to dict


def test_persist(scrape):
    scrape.persist()
    assert scrape.db.create_table.called
    assert scrape.db.insert_records.called
