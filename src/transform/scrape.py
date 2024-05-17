import json
import re
from abc import ABC
from dataclasses import dataclass, field, fields
from datetime import date, datetime
from typing import TypeVar, Never

from dateutil.relativedelta import relativedelta
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from database import Database
from transform.schema import age_distribution_schema, top_countries_traffic_schema, visits_history_schema

T = TypeVar("T")

_VALID_DOMAIN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$")


class ValidationException(Exception):
    """Raised when an error is encountered during validation."""


def _to_sec(time_hms: str) -> int | None:
    """Get value in seconds from hh:mm:ss time string."""
    if time_hms:
        h, m, s = time_hms.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    return None


def _to_float(percent_value: str) -> float | None:
    """Get float value from percent string."""
    if percent_value:
        return float(percent_value.removesuffix("%")) / 100
    return None


def _age_dist_key(bucket: dict[str, int | float]) -> str:
    """
    Generate a key representing an age distribution bucket.

    :param bucket: A dictionary representing an age distribution bucket, containing keys 'minAge' and 'maxAge'.
    :return: A string representing the age range covered by the bucket.
    """
    min_age = bucket.get("minAge")
    if max_age := bucket.get("maxAge"):
        return f"{min_age} - {max_age}"
    else:
        return f"{min_age}+"


def _validate(value: str | None, t: type[T], field_name: str) -> T | None:
    """
    Validates a string value and converts it to the expected type.

    :param value: String value to validate.
    :param t: The expected type.
    :param field_name: Name of the field
    :return: The converted value.
    """
    if value is None:
        return None
    elif isinstance(value, str):
        try:
            return t(value)
        except ValueError as e:
            raise ValidationException(f"'{field_name}' must be of type '{t.__name__}': {str(e)}.")
    else:
        raise ValidationException(f"'{field_name}' must be of type '{t.__name__}'!")


def _validate_json(value: str | None, field_name: str, default: list[Never] | dict[Never]) -> list | dict:
    """
    Validates a json string.

    :param value: Json string to validate.
    :param field_name: Name of the field.
    :param default: The Default value for the field can be either an empty list or an empty dictionary.
    :return: The converted value.
    """
    if value is None:
        return default
    elif isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError as e:
            raise ValidationException(f"'{field_name}' is not a valid json string: {str(e)}")
    else:
        raise ValidationException(f"'{field_name}' is not a valid json string, got '{type(value).__name__}' instead!")


@dataclass
class Validator(ABC):

    def __post_init__(self) -> None:
        """
        Run validation methods if declared. The validation method can "validate" the value by converting it to the
        expected type and returning it, or by raising an exception.
        The validation is performed by calling the method with signature `_validate_<field.name>(self) -> field.type`.

        :return: None
        """
        for f in fields(self):
            if method := getattr(self, f"_validate_{f.name}", None):
                setattr(self, f.name, method())


@dataclass
class Scrape(Validator):
    """
    Represents a website scrape and provides methods to process and persist scrape data.
    This class processes website scrape-data and persists it into a database.

    :param domain: The domain of the website.
    :param snapshot_date: The date of the snapshot.
    :param global_rank: The global rank of the website.
    :param total_visits: The total number of visits to the website.
    :param bounce_rate: The bounce rate of the website.
    :param pages_per_visit: The average number of pages per visit to the website.
    :param avg_visit_duration: The average visit duration of the website.
    :param one_month_rank_change: The change in global rank over one month.
    :param two_month_rank_change: The change in global rank over two months.
    :param visits_history: The history of visits to the website.
    :param last_month_change_in_traffic: The change in traffic over the last month.
    :param top_countries: The top countries who visited the website.
    :param age_distribution: The age distribution of visitors to the website.
    :param db: The database instance to use. If not provided, a new instance will be created by default.
    """
    domain: str
    snapshot_date: date
    global_rank: int | None
    total_visits: int | None
    bounce_rate: float | None
    pages_per_visit: float | None
    avg_visit_duration: int | None
    one_month_rank_change: int | None
    two_month_rank_change: int | None
    visits_history: dict[str, int]
    last_month_change_in_traffic: float | None
    top_countries: list[str]
    age_distribution: dict[str, float]
    db: Database | None = field(default_factory=lambda: Database())

    def _validate_domain(self) -> str:
        if not isinstance(self.domain, str):
            raise ValidationException(f"'domain' must be of type 'str', got '{type(self.domain).__name__}' instead!")
        elif not _VALID_DOMAIN.match(self.domain):
            raise ValidationException("Not a valid domain!")
        else:
            return self.domain

    def _validate_snapshot_date(self) -> date:
        try:
            return datetime.fromisoformat(self.snapshot_date).date()
        except (TypeError, ValueError) as e:
            raise ValidationException(f"'snapshot_date' is not a valid date: {str(e)}")

    def _validate_global_rank(self) -> int | None:
        return _validate(value=self.global_rank, t=int, field_name="global_rank")

    def _validate_total_visits(self) -> int | None:
        return _validate(value=self.total_visits, t=int, field_name="total_visits")

    def _validate_bounce_rate(self) -> float | None:
        if self.bounce_rate is None:
            return None
        elif type(self.bounce_rate) is str:
            try:
                return _to_float(self.bounce_rate)
            except ValueError as e:
                raise ValidationException(f"'bounce_rate' is not a valid percentage: {str(e)}.")
        else:
            raise ValidationException("'bounce_rate' is not a valid percentage!")

    def _validate_pages_per_visit(self) -> float | None:
        return _validate(value=self.pages_per_visit, t=float, field_name="pages_per_visit")

    def _validate_avg_visit_duration(self) -> int | None:
        if self.avg_visit_duration is None:
            return None
        elif isinstance(self.avg_visit_duration, str):
            try:
                return _to_sec(self.avg_visit_duration)
            except ValueError as e:
                raise ValidationException(f"'avg_visit_duration' is not a valid time string of the format 'hh:mm:ss': "
                                          f"{str(e)}")
        else:
            raise ValidationException(f"'avg_visit_duration' is not a string, "
                                      f"got '{type(self.avg_visit_duration).__name__}' instead!")

    def _validate_one_month_rank_change(self) -> int | None:
        return _validate(value=self.one_month_rank_change, t=int, field_name="one_month_rank_change")

    def _validate_two_month_rank_change(self) -> int | None:
        return _validate(value=self.two_month_rank_change, t=int, field_name="two_month_rank_change")

    def _validate_visits_history(self) -> dict[str, int]:
        if self.visits_history is None:
            return {}
        try:
            visits_history = json.loads(self.visits_history)
            validate(instance=visits_history, schema=visits_history_schema)
            return visits_history
        except (TypeError, ValueError, ValidationError) as e:
            raise ValidationException(f"'visits_history' is not a valid json string: {str(e)}") from e

    def _validate_last_month_change_in_traffic(self) -> float | None:
        return _validate(value=self.last_month_change_in_traffic, t=float, field_name="last_month_change_in_traffic")

    def _validate_top_countries(self) -> list[str]:
        if self.top_countries is None:
            return []
        try:
            top_countries = json.loads(self.top_countries)
            validate(instance=top_countries, schema=top_countries_traffic_schema)
            return [c["countryAlpha2Code"] for c in top_countries]
        except (TypeError, ValueError, ValidationError) as e:
            raise ValidationException(f"'top_countries' is not a valid json string: {str(e)}") from e

    def _validate_age_distribution(self) -> dict[str, float]:
        if self.age_distribution is None:
            return {}
        try:
            age_distribution = json.loads(self.age_distribution)
            validate(instance=age_distribution, schema=age_distribution_schema)
            return {_age_dist_key(a): a["value"] for a in age_distribution}
        except (TypeError, ValueError, ValidationError) as e:
            raise ValidationException(f"'age_distribution' is not a valid json string: {str(e)}") from e

    def _create_website_scrapes_table(self) -> None:
        """Create the 'website_scrapes' table in the database."""
        self.db.create_table(
            table="website_scrapes",
            schema=[
                ("website", "TEXT"),
                ("snapshot_date", "TEXT"),
                ("global_rank", "INTEGER"),
                ("total_visits", "INTEGER"),
                ("bounce_rate", "REAL"),
                ("pages_per_visit", "REAL"),
                ("avg_visit_duration", "INTEGER"),
                ("last_month_change_in_traffic", "REAL")
            ],
            primary_key=["website", "snapshot_date"]
        )

    def _create_website_global_rank_table(self) -> None:
        """Create the 'website_global_rank' table in the database."""
        self.db.create_table(
            table="website_global_rank",
            schema=[
                ("website", "TEXT"),
                ("snapshot_date", "TEXT"),
                ("global_rank", "INTEGER"),
            ],
            primary_key=["website", "snapshot_date"]
        )

    def _create_website_total_visits_table(self) -> None:
        """Create the 'website_total_visits' table in the database."""
        self.db.create_table(
            table="website_total_visits",
            schema=[
                ("website", "TEXT"),
                ("snapshot_date", "TEXT"),
                ("total_visits", "INTEGER"),
            ],
            primary_key=["website", "snapshot_date"]
        )

    def _create_top_countries_table(self) -> None:
        """Create the 'top_countries' table in the database."""
        self.db.create_table(
            table="top_countries",
            schema=[
                ("website", "TEXT"),
                ("snapshot_date", "TEXT"),
                ("country", "TEXT"),
            ],
            primary_key=["website", "snapshot_date", "country"]
        )

    def _create_age_distribution_table(self) -> None:
        """Create the 'age_distribution' table in the database."""
        self.db.create_table(
            table="age_distribution",
            schema=[
                ("website", "TEXT"),
                ("snapshot_date", "TEXT"),
                ("age_group_label", "TEXT"),
                ("value", "REAL")
            ],
            primary_key=["website", "snapshot_date", "age_group_label"]
        )

    def _to_website_scrapes_table(self):
        """Write data to the 'website_scrapes' table in the database."""
        self._create_website_scrapes_table()
        self.db.insert_records(
            table="website_scrapes",
            records=[(
                self.domain,
                self.snapshot_date.isoformat(),
                self.global_rank,
                self.total_visits,
                self.bounce_rate,
                self.pages_per_visit,
                self.avg_visit_duration,
                self.last_month_change_in_traffic
            )]
        )

    def _to_website_global_rank_table(self) -> None:
        """Write data to the 'website_global_rank' table in the database."""
        self._create_website_global_rank_table()
        prev_1_month = self.snapshot_date - relativedelta(months=1)
        prev_2_month = self.snapshot_date - relativedelta(months=2)
        self.db.insert_records(
            table="website_global_rank",
            records=[
                (self.domain, self.snapshot_date.isoformat(), self.global_rank),
                (self.domain, prev_1_month.isoformat(), self.global_rank + self.one_month_rank_change),
                (self.domain, prev_2_month.isoformat(), self.global_rank - self.two_month_rank_change),
            ]
        )

    def _to_website_total_visits_table(self) -> None:
        """Write data to the 'website_total_visits' table in the database."""
        self._create_website_total_visits_table()
        self.db.insert_records(
            table="website_total_visits",
            records=[(self.domain, v_date, v_count) for v_date, v_count in self.visits_history.items()]
        )

    def _to_top_countries_table(self) -> None:
        """Write data to the 'top_countries' table in the database."""
        self._create_top_countries_table()
        self.db.insert_records(
            table="top_countries",
            records=[(self.domain, self.snapshot_date.isoformat(), c) for c in self.top_countries]
        )

    def _to_age_distribution_table(self) -> None:
        """Write data to the 'age_distribution' table in the database."""
        self._create_age_distribution_table()
        self.db.insert_records(
            table="age_distribution",
            records=[(self.domain, self.snapshot_date.isoformat(), age_group_label, value)
                     for age_group_label, value in self.age_distribution.items()]
        )

    def persist(self):
        """Persist scrape data into the database."""
        self._to_website_scrapes_table()
        self._to_website_global_rank_table()
        self._to_website_total_visits_table()
        self._to_top_countries_table()
        self._to_age_distribution_table()
