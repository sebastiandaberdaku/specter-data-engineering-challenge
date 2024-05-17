import re

import matplotlib.pyplot as plt

from analyse.analyse import (
    calculate_month_on_month_website_total_visits_growth,
    calculate_month_on_month_website_global_rank_growth,
    rank_websites_on_relative_total_visits_growth,
)


def plot_rank_websites_on_relative_total_visits_growth(out_path: str = "./resources") -> None:
    """
    Plots and saves a bar chart showing the growth percentages of website traffic, ranked by their relative total visits
    growth.

    :param out_path: The directory where the plot image will be saved. Default is "./resources".
    :return: None
    """
    data = rank_websites_on_relative_total_visits_growth()

    # Extracting website names, growth percentages, and ranks
    websites = [item[0] for item in data]
    growth_percentages = [item[1] for item in data]
    ranks = [item[2] for item in data]

    # Plotting
    fig, ax = plt.subplots()

    bars = ax.bar(websites, growth_percentages, color=["green" if x > 0 else "red" for x in growth_percentages])

    # Adding labels and title
    ax.set_xlabel("Websites")
    ax.set_ylabel("Growth Percentage (%)")
    ax.set_title("Website Traffic Growth Percentage")
    ax.axhline(0, color="grey", linewidth=0.8)  # Adding a horizontal line at y=0 for reference

    # Adding the rank as text on top of the bars
    for bar, rank in zip(bars, ranks):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, f"#{rank}", ha="center", va="bottom" if yval < 0 else "top",
                color="black")

    # Show plot
    plt.xticks(rotation=45)  # Rotate x-axis labels if needed
    plt.tight_layout()  # Adjust layout to make room for labels
    plt.savefig(f"{out_path}/website_traffic_rank.png", dpi=300)  # Save plot as PNG
    plt.show()


def plot_month_on_month_growth(data: list[tuple], plot_title: str, out_path: str = "./resources") -> None:
    """
    Plots and saves a line chart showing month-on-month growth percentages for multiple websites.

    :param data: A list of tuples where each tuple contains: (website_name, date, _, _, growth_percentage).
    :param plot_title: The title of the plot.
    :param out_path: The directory where the plot image will be saved. Default is "./resources".
    :return: None
    """
    # Extracting data for each website
    websites = {}
    for entry in data:
        website, date, _, _, growth_percentage = entry

        if website not in websites:
            websites[website] = {
                "dates": [],
                "growth_percentages": []
            }

        websites[website]["dates"].append(date)
        websites[website]["growth_percentages"].append(growth_percentage)

    # Plotting
    for website, info in websites.items():
        plt.plot(info["dates"], info["growth_percentages"], marker="o", label=website)

    # Adding labels and title
    plt.xlabel("Date")
    plt.ylabel("Growth Percentage [%]")
    plt.title(plot_title)
    plt.legend(loc="upper right")
    plt.xticks(rotation=45)  # Rotate x-axis labels if needed

    filename = re.sub(r"\s+", "_", plot_title.lower())
    # Show plot
    plt.tight_layout()  # Adjust layout to make room for labels
    plt.grid(True)  # Add grid for better readability
    plt.savefig(f"{out_path}/{filename}.png", dpi=300)  # Save plot as PNG
    plt.show()


def plot_month_on_month_website_total_visits_growth() -> None:
    """
    Plots and saves a line chart showing month-on-month total visits growth for websites.

    :return: None
    """
    data = calculate_month_on_month_website_total_visits_growth()
    plot_month_on_month_growth(data=data, plot_title="Website Total Visits Growth")


def plot_month_on_month_website_global_rank_growth() -> None:
    """
    Plots and saves a line chart showing month-on-month global rank growth for websites.

    :return: None
    """
    data = calculate_month_on_month_website_global_rank_growth()
    plot_month_on_month_growth(data=data, plot_title="Website Global Rank Growth")
