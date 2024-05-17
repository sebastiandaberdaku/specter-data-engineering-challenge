import os
import zipfile
from contextlib import contextmanager

import pytest

from extract.extract import (
    download_file,
    extract_data_points,
    get_html_files,
    parse_html_file,
    to_csv,
    unzip_file,
)


@pytest.fixture
def mock_requests_get(monkeypatch):
    # Define a mock function that will be used to replace requests.get
    @contextmanager
    def mock_get(url, **kwargs):
        # Mock response object
        class MockResponse:
            def __init__(self):
                # Simulate response content
                self.content = [b'mocked data', b'some more mocked data', b'another piece of mocked data']

            def iter_content(self, chunk_size=1, decode_unicode=False):
                return iter(self.content)

            def raise_for_status(self):
                pass

        yield MockResponse()

    # Patch requests.get with the mock function
    monkeypatch.setattr("requests.get", mock_get)


def test_download_file(tmp_path, mock_requests_get):
    # Download a sample file
    download_url = "https://www.example.com/sample.zip"
    download_dest = f"{tmp_path}/sample.zip"
    download_file(download_url, download_dest)

    # Assert that the file was downloaded successfully
    assert os.path.exists(download_dest)


def test_unzip_file(tmp_path):
    # Create a sample zip file
    zip_path = f"{tmp_path}/test.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.writestr("file1.txt", "Hello World!")
        zipf.writestr("file2.txt", "How are you?")

    # Unzip the files
    unzip_file(zip_path, tmp_path)

    # Assert that the files were unzipped successfully
    assert os.path.exists(f"{tmp_path}/file1.txt")
    assert os.path.exists(f"{tmp_path}/file2.txt")


def test_get_html_files(tmp_path):
    # Create sample HTML files
    html_files = ["test1.html", "test2.html"]
    for html_file in html_files:
        open(f"{tmp_path}/{html_file}", "w").close()

    # Test get_html_files function
    result = get_html_files(tmp_path)

    # Assert that the HTML files were retrieved successfully
    assert len(result) == len(html_files)
    for html_file in html_files:
        assert f"{tmp_path}/{html_file}" in result


def test_parse_html_file(tmp_path):
    # Create a sample HTML file with window.__APP_DATA__
    html_file = f"{tmp_path}/test.html"
    with open(html_file, "w") as f:
        f.write("<script>\n"
                "window.__APP_DATA__ = {'key': 'value'}\n"
                "window.__APP_METADATA__ = {'otherKey': 'otherValue'}\n"
                "</script>")

    # Test parse_html_file function
    result = parse_html_file(html_file)

    # Assert that the correct JSON content was extracted
    assert result == "{'key': 'value'}"


@pytest.fixture
def sample_json_data():
    return """
    {
        "layout": {
            "data": {
                "domain": "example.com",
                "snapshotDate": "2022-01-01",
                "overview": {
                    "globalRank": 1000,
                    "visitsTotalCount": 5000,
                    "bounceRateFormatted": "50%",
                    "pagesPerVisit": 3.5,
                    "visitsAvgDurationFormatted": "00:05:30",
                    "globalRankChange": 50
                },
                "ranking": {
                    "globalRankChange": 30
                },
                "traffic": {
                    "visitsHistory": {"2021-10": 3000, "2021-11": 3500, "2021-12": 4000},
                    "visitsTotalCountChange": 200
                },
                "geography": {
                    "topCountriesTraffics": [{"countryAlpha2Code": "US", "trafficPercentage": 40},
                                             {"countryAlpha2Code": "IN", "trafficPercentage": 20}]
                },
                "demographics": {
                    "ageDistribution": [{"minAge": 18, "maxAge": 30, "value": 50},
                                        {"minAge": 31, "maxAge": 50, "value": 30}]
                }
            }
        }
    }
    """


def test_extract_data_points(sample_json_data):
    # Call the function
    result = extract_data_points(sample_json_data)

    # Check the extracted data
    assert result["domain"] == "example.com"
    assert result["snapshot_date"] == "2022-01-01"
    assert result["global_rank"] == 1000
    assert result["total_visits"] == 5000
    assert result["bounce_rate"] == "50%"
    assert result["pages_per_visit"] == 3.5
    assert result["avg_visit_duration"] == "00:05:30"
    assert result["one_month_rank_change"] == 50
    assert result["two_month_rank_change"] == 30
    assert result["visits_history"] == '{"2021-10": 3000, "2021-11": 3500, "2021-12": 4000}'
    assert result["last_month_change_in_traffic"] == 200
    assert result["top_countries"] == ('[{"countryAlpha2Code": "US", "trafficPercentage": 40}, '
                                       '{"countryAlpha2Code": "IN", "trafficPercentage": 20}]')
    assert result["age_distribution"] == ('[{"minAge": 18, "maxAge": 30, "value": 50}, '
                                          '{"minAge": 31, "maxAge": 50, "value": 30}]')


def test_to_csv(tmp_path):
    # Create sample data points
    data_points = [
        {"domain": "example1.com", "snapshot_date": "2022-01-01"},
        {"domain": "example2.com", "snapshot_date": "2022-01-02"}
    ]
    output_file = f"{tmp_path}/output.csv"

    # Test to_csv function
    to_csv(data_points, output_file)

    # Assert that the CSV file was created successfully
    assert os.path.exists(output_file)

    # Assert that the CSV file contains the correct data
    with open(output_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == len(data_points) + 1  # Plus 1 for the header row
        assert "domain,snapshot_date\n" in lines
        assert "example1.com,2022-01-01\n" in lines
        assert "example2.com,2022-01-02\n" in lines
