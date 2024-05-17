from analyse import (
    plot_month_on_month_website_global_rank_growth,
    plot_month_on_month_website_total_visits_growth,
    plot_rank_websites_on_relative_total_visits_growth,
)
from extract import export_url_content_to_csv
from transform import load_csv_to_db


def main() -> None:
    """
    Runs the steps required by the challenge.

    :return: None
    """
    # Url of the zip archive with the website scrapes
    url = ("https://drive.usercontent.google.com/download?"
           "id=1L0LcBvWzxIfSP2JDb5LbXIHZM_KS3lVq&"
           "export=download&"
           "authuser=0")
    csv_path = "./resources/output.csv"
    # Downloads the zip archive, unzips it, parses the html content and then saves it to ./resources/output.csv
    export_url_content_to_csv(url=url, output_file=csv_path)

    # Loads the content of the csv file into a SQLite3 Database
    load_csv_to_db(csv_file=csv_path)

    # Perform the analysis and plot the results
    plot_month_on_month_website_global_rank_growth()
    plot_month_on_month_website_total_visits_growth()
    plot_rank_websites_on_relative_total_visits_growth()


if __name__ == "__main__":
    main()
