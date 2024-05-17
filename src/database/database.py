import logging
import sqlite3
from functools import wraps
from sqlite3 import Cursor
from typing import Callable, Any

logger = logging.getLogger(__name__)


class _SQLite3Singleton(type):
    """
    Metaclass implementing the Singleton design pattern for SQLite3 database connections.

    This metaclass ensures that only one instance of a class derived from it is created for each unique database path.
    If multiple instances are requested with the same database path, the same instance will be returned.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        database_path = args[0] if args else kwargs.get("database_path")
        if database_path not in cls._instances:
            cls._instances[database_path] = super(_SQLite3Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[database_path]


def _with_cursor(func: Callable) -> Callable:
    """
    Decorator to automatically manage cursor creation and transaction handling for methods that interact with a
    database.

    This decorator ensures that a cursor is created for each decorated method and that the transaction is committed
    automatically after the method execution. It is designed to be used within classes where the `self.connection`
    attribute refers to an SQLite3 database connection.

    :param func: The method to be decorated.
    :return: The decorated method.
    """

    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        conn = self.connection
        with conn:  # automatically commits transaction when done
            cur = conn.cursor()
            return func(self, cur, *args, **kwargs)

    return wrapper


class Database(metaclass=_SQLite3Singleton):
    """
    Class representing an SQLite3 database connection with convenient methods for database operations.

    This class provides methods for creating tables, inserting records, executing SQL queries,
    and managing the database connection.
    """

    def __init__(self, database_path: str = "./resources/sqlite.db") -> None:
        """
        Initialize the Database instance with an SQLite3 database connection.

        :param database_path: The path to the SQLite3 database file.
        """
        logger.info(f"Initializing database connection to path '{database_path}'...")
        self.connection = sqlite3.connect(database=database_path)
        logger.info("Database connection initialized!")

    def __del__(self) -> None:
        """
        Destructor to close the database connection when the instance is deleted.

        :return: None
        """
        if self.connection is not None:
            logger.info("Closing database connection...")
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed!")

    def __bool__(self) -> bool:
        """
        :return: True if the database connection is open, False otherwise.
        """
        return self.connection is not None

    @_with_cursor
    def create_table(self, cur: Cursor, table: str, schema: list[tuple[str, str]],
                     primary_key: list[str] | None = None) -> None:
        """
        Create a table in the database if it does not already exist with the specified schema.

        :param cur: The SQLite3 cursor object (automatically injected).
        :param table: The name of the table to create.
        :param schema: A list of tuples specifying the column names and their corresponding data types.
        :param primary_key: A list of column names to define as the primary key.
        :return: None
        """
        string_schema = ", ".join(f"{fname} {ftype}" for fname, ftype in schema)
        if primary_key:
            primary_key_clause = f"CONSTRAINT pk PRIMARY KEY ({', '.join(primary_key)})"
            string_schema += ", " + primary_key_clause
        sql = f"CREATE TABLE IF NOT EXISTS {table} ({string_schema});"
        logger.info(f"SQL statement: {sql}")
        cur.execute(sql)

    @_with_cursor
    def _get_table_column_names(self, cur: Cursor, table: str) -> list[str]:
        """
        Retrieve the column names of a table.

        :param cur: The SQLite3 cursor object (automatically injected).
        :param table: The name of the table.
        :return: A list of column names.
        """
        cur.execute(f"SELECT * FROM {table} LIMIT 0;")
        column_names = [desc[0] for desc in cur.description]
        return column_names

    @_with_cursor
    def insert_records(self, cur: Cursor, table: str, records: list[tuple]) -> None:
        """
        Insert records into a table.

        :param cur: The SQLite3 cursor object (automatically injected).
        :param table: The name of the table.
        :param records: A list of tuples representing records to insert.
        :return: None
        """
        column_names = self._get_table_column_names(table=table)
        cols = ", ".join(f'"{c}"' for c in column_names)
        vals = ", ".join(["?"] * len(column_names))
        sql = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({vals});"
        logger.info(f"SQL statement: {sql}")
        cur.executemany(sql, records)

    @_with_cursor
    def execute_sql(self, cur: Cursor, sql: str) -> list[tuple]:
        """
        Execute an SQL query.

        :param cur: The SQLite3 cursor object (automatically injected).
        :param sql: The SQL query to execute.
        :return: A list of tuples representing the query results.
        """
        cur.execute(sql)
        if cur.description:
            return cur.fetchall()
        else:
            return []
