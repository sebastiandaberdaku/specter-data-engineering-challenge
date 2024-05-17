import csv
import logging
from typing import Any

from transform.scrape import Scrape, ValidationException

logger = logging.getLogger(__name__)


def load_csv(csv_file: str) -> list[dict[str, Any]]:
    """
    Load data from a CSV file and return it as a list of dictionaries.
    Each dictionary represents a row in the CSV file, with keys as column names
    and values as corresponding values in the row.

    :param csv_file: Path to the CSV file.
    :return: List of dictionaries representing the CSV data.
    """
    with open(csv_file, "r") as csv_file:
        return list(csv.DictReader(csv_file))


def load_csv_to_db(csv_file: str) -> None:
    """
    Load data from a CSV file and insert it into the database.
    :param csv_file: Path to the CSV file.
    :return: None
    """
    csv_data = load_csv(csv_file)
    for row in csv_data:
        try:
            Scrape(**row).persist()
        except ValidationException as e:
            logger.error(f"An error occurred while parsing row '{row}'!", exc_info=e)
