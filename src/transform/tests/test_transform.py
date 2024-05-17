import csv

import pytest

from transform.transform import load_csv


@pytest.fixture
def sample_csv(tmp_path):
    # Create a sample CSV file for testing
    csv_data = [
        {"Name": "John", "Age": 30, "City": "New York"},
        {"Name": "Alice", "Age": 25, "City": "Los Angeles"},
    ]
    file_path = tmp_path / "test.csv"
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Name", "Age", "City"])
        writer.writeheader()
        writer.writerows(csv_data)
    return str(file_path)


def test_load_csv(sample_csv):
    # Load the sample CSV file
    data = load_csv(sample_csv)
    # Check if data is loaded correctly
    assert len(data) == 2
    assert data[0]["Name"] == "John"
    assert data[0]["Age"] == "30"
    assert data[1]["City"] == "Los Angeles"
