from database import Database


def calculate_month_on_month_growth(table: str, column: str, db: Database | None = None) -> list[tuple]:
    """
    Calculates the month-on-month growth percentage for a specified column in a database table.

    :param table: The name of the database table.
    :param column: The name of the column for which the month-on-month growth is to be calculated.
    :param db: The database object.
    :return: A list of tuples containing the website, snapshot date, current value, previous value, and the percentage
        change between the current and previous values.
    """
    db = db or Database()
    # The SQL query uses window functions (LAG) to compute the previous value of the specified column for each
    # website and calculates the month-on-month growth percentage based on the current and previous values.
    sql = f"""
    SELECT
        website,
        snapshot_date,
        val,
        prev_val,
        CASE 
            WHEN prev_val IS NOT NULL THEN (val - prev_val) * 100.0 / prev_val
            ELSE NULL
        END AS val_change_percentage
    FROM (
        SELECT
            website,
            snapshot_date,
            {column} AS val,
            LAG({column}) OVER (PARTITION BY website ORDER BY snapshot_date) AS prev_val
        FROM {table}
    )
    WHERE
        prev_val IS NOT NULL
    ORDER BY
        website,
        snapshot_date;
    """
    return db.execute_sql(sql)


def calculate_month_on_month_website_global_rank_growth(db: Database | None = None) -> list[tuple]:
    """
    Calculates the month-on-month growth percentage for the global rank in a database table.

    :param db: The database object.
    :return: A list of tuples containing the website, snapshot date, current global rank, previous month's global rank,
        and the percentage change between the current and previous values.
    """
    return calculate_month_on_month_growth(table="website_global_rank", column="global_rank", db=db)


def calculate_month_on_month_website_total_visits_growth(db: Database | None = None) -> list[tuple]:
    """
    Calculates the month-on-month growth percentage for the total visits in a database table.

    :param db: The database object.
    :return: A list of tuples containing the website, snapshot date, current total visits, previous month's total
        visits, and the percentage change between the current and previous values.
    """
    return calculate_month_on_month_growth(table="website_total_visits", column="total_visits", db=db)


def rank_websites_on_relative_total_visits_growth(db: Database | None = None) -> list[tuple]:
    """
    Ranks websites based on relative total visits growth.
    This function calculates the growth percentage of total visits for each website and ranks them accordingly.

    :param db: Optional Database instance. If not provided, a new instance will be created.
    :return: A list of tuples containing website name, growth percentage, and rank.
    """
    db = db or Database()
    sql = """
    WITH ranked_visits AS (
        SELECT
            website,
            snapshot_date,
            total_visits,
            ROW_NUMBER() OVER (PARTITION BY website ORDER BY snapshot_date) AS row_num_asc,
            ROW_NUMBER() OVER (PARTITION BY website ORDER BY snapshot_date DESC) AS row_num_desc
        FROM website_total_visits
    ),
    visit_changes AS (
        SELECT
            r1.website,
            r1.total_visits AS first_visits,
            r2.total_visits AS last_visits
        FROM ranked_visits r1
        JOIN ranked_visits r2 ON r1.website = r2.website AND r1.row_num_asc = 1 AND r2.row_num_desc = 1
    ),
    growth_calculations AS (
        SELECT
            website,
            (last_visits - first_visits) * 100.0 / first_visits AS growth_percentage
        FROM visit_changes
        WHERE first_visits IS NOT NULL AND last_visits IS NOT NULL
    )
    SELECT
        website,
        growth_percentage,
        RANK() OVER (ORDER BY growth_percentage DESC) AS rank
    FROM growth_calculations
    ORDER BY rank;
    """
    return db.execute_sql(sql)
