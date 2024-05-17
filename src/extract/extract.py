import csv
import glob
import json
import logging
import re
import zipfile
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
_APP_DATA_PATTERN = re.compile(r"\s*window\.__APP_DATA__ = (.*)")
_CHUNK_SIZE = 100 * 1024  # 100KiB


def download_file(url: str, destination_file: str) -> None:
    """
    Downloads a file to a given destination.

    :param url: Url of the file to download.
    :param destination_file: Destination file name
    :return: None
    """
    with requests.get(url=url, stream=True) as r:
        r.raise_for_status()
        with open(destination_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=_CHUNK_SIZE):
                f.write(chunk)


def unzip_file(source_file: str, destination_folder: str) -> None:
    """
    Unzips a zip file to a given destination.

    :param source_file: Source Zip file.
    :param destination_folder: Destination folder
    :return: None
    """
    with zipfile.ZipFile(source_file, "r") as zf:
        zf.extractall(destination_folder)


def get_html_files(folder_path: str) -> list[str]:
    """
    Get a list of HTML files in the specified folder.
    This function searches for HTML files within the specified folder and returns a list of their paths.

    :param folder_path: The path to the folder to search for HTML files.
    :return: A list of paths to HTML files found in the folder.
    """
    return glob.glob(pathname=f"{folder_path}/*.html", recursive=False)


def parse_html_file(file_path: str) -> str:
    """
    Extracts the "window.__APP_DATA__" json from the given HTML file.

    :param file_path: Path to the HTML file to parse.
    :return: The json content of window.__APP_DATA__.
    """
    logger.info(f"Parsing HTML file {file_path}.")
    with open(file_path, "r") as in_file:
        html_content = in_file.read()
        soup = BeautifulSoup(html_content, features="html.parser")
        # The information we are interested in is located in a script element of the input HTML file.
        app_data = soup.select_one("script:-soup-contains('window.__APP_DATA__')")
        # Extract the json string with a simple regex.
        if app_data and (match := _APP_DATA_PATTERN.match(app_data.string)):
            return match.group(1)
        else:
            raise ValueError(f"Failed parsing {file_path}!")


def extract_data_points(json_data: str) -> dict[str, Any]:
    """
    Extracts data points from JSON data representing website analytics.
    This function takes JSON data representing website analytics, extracts various data points, and returns them as a
    dictionary.

    :param json_data: JSON data representing website analytics.
    :return: A dictionary containing various extracted data points.
    """
    data = json.loads(json_data).get("layout", {}).get("data", {})
    overview = data.get("overview", {})
    ranking = data.get("ranking", {})
    traffic = data.get("traffic", {})
    result = {
        "domain": data["domain"],
        "snapshot_date": data["snapshotDate"],
        # a. Global Rank
        "global_rank": overview.get("globalRank"),
        # b. Total Visits
        "total_visits": overview.get("visitsTotalCount"),
        # c. Bounce Rate
        "bounce_rate": overview.get("bounceRateFormatted"),
        # d. Pages per Visit
        "pages_per_visit": overview.get("pagesPerVisit"),
        # e. Avg Visit Duration
        "avg_visit_duration": overview.get("visitsAvgDurationFormatted"),
        # f. The change in rank over October, November and December
        "one_month_rank_change": overview.get("globalRankChange"),
        # f. The change in rank over October, November and December
        "two_month_rank_change": ranking.get("globalRankChange"),
        # g. The total number of visits in October, November and December
        "visits_history": json.dumps(traffic.get("visitsHistory", {})),
        # h. Last Month Change in traffic
        "last_month_change_in_traffic": traffic.get("visitsTotalCountChange"),
        # i. Top Countries
        "top_countries": json.dumps(data.get("geography", {}).get("topCountriesTraffics", [])),
        # j. Age Distribution
        "age_distribution": json.dumps(data.get("demographics", {}).get("ageDistribution", []))
    }
    return result


def to_csv(data_points: list[dict[str, Any]], output_file: str) -> None:
    """
    Write a list of dictionaries to a CSV file.
    This function writes a list of dictionaries, where each dictionary represents a row of data, to a CSV file.

    :param data_points: A list of dictionaries representing data points.
    :param output_file: The path to the output CSV file.
    :return: None
    """
    with open(output_file, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data_points[0].keys())
        writer.writeheader()
        for row in data_points:
            writer.writerow(row)


def export_url_content_to_csv(
        url: str,
        download_dest: str = "./resources/scrapes.zip",
        unzipped_dest: str = "./resources/unzipped",
        output_file: str = "./resources/output.csv",
) -> str:
    """
    Export URL content to a CSV file.

    This function downloads a file from the specified URL, unzips it, extracts data points from HTML files within the
    unzipped folder, and writes the data points to a CSV file.

    :param url: The URL from which to download the content.
    :param download_dest: The destination path to save the downloaded file.
    :param unzipped_dest: The destination folder to unzip the downloaded file.
    :param output_file: The path to the output CSV file.
    :return: None
    """
    download_file(url=url, destination_file=download_dest)
    unzip_file(source_file=download_dest, destination_folder=unzipped_dest)
    html_files = get_html_files(folder_path=unzipped_dest)
    raw_app_data = [parse_html_file(h) for h in html_files]
    data_points = [extract_data_points(d) for d in raw_app_data]
    to_csv(data_points=data_points, output_file=output_file)
