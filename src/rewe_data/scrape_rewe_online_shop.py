import os
import sys
import pandas as pd
import tqdm
import argparse

from src.edge_browser_driver.loader import load_driver
from src.rewe_data.page_navigation import (
    go_next_page,
    go_back,
    get_number_of_product_categories,
    random_sleep,
    go_to_next_category,
    get_number_of_pages,
)
from src.rewe_data.scraping import scrape_product_category_data_from_page

parser = argparse.ArgumentParser()
parser.add_argument(
    "--extract_nutrition", help="Extract Nutrition Data", default=False, type=bool
)
parser.add_argument(
    "--output_path",
    help="Where to story your scraped dataset",
    default="data/raw/rewe_dataset.csv",
)
parser.add_argument("--remote_debugging_port", help="Debugging Port", default=9222)
parser.add_argument(
    "--edge_driver_path",
    help="Path to Edge Driver",
    default="C:\\Users\\arthu\\Tools\\WebDriver\\edgedriver_win64\\msedgedriver.exe",
)
parser.add_argument(
    "--url", help="URL to the Rewe Website", default="https://shop.rewe.de/"
)
args = parser.parse_args()


def main():
    driver = load_driver(vars(args))

    visited_category_names = []
    page_dfs = []
    n_categories = get_number_of_product_categories(driver)

    category_bar = tqdm.tqdm(
        total=n_categories, desc="Product Categories", leave=True, position=0
    )

    while True:
        random_sleep(0, 1)
        next_category_name = go_to_next_category(driver, visited_category_names)
        if next_category_name == False:
            break
        visited_category_names.append(next_category_name)

        category_bar.update(1)

        n_pages = get_number_of_pages(driver)

        page_bar = tqdm.tqdm(total=n_pages, desc="Pages", leave=False, position=1)

        while True:
            page_bar.update(1)

            page_df = scrape_product_category_data_from_page(
                driver=driver,
                page_source=driver.page_source,
                category=next_category_name,
                extract_nutrition=args.extract_nutrition,
            )
            page_dfs.append(page_df)

            if go_next_page(driver) == False:
                break

        while True:
            if go_back(driver) == False:
                break

    dfs = pd.concat(page_dfs, ignore_index=True)
    dfs.to_csv(args.output_path)
    dfs.reset_index(drop=True, inplace=True)
    driver.close()


if __name__ == "__main__":
    main()
