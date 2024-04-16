import os
import sys
import pandas as pd
import tqdm

sys.path.append("..")
#os.chdir(os.path.join(os.getcwd(), ".."))

from src.rewe_data_scraper import load_driver, go_to_next_category, scrape_product_category_data, go_next_page, go_back, extract_product_data
from src.rewe_data_scraper import get_number_of_product_categories, get_number_of_pages, random_sleep
from src.gpt_extract_product_data import scrape_product_category_data

output_path = "data/rewe_dataset.csv"
driver = load_driver(config_path="config/rewe_browser_config.json")

visited_category_names = []
page_dfs = []
n_categories = get_number_of_product_categories(driver)

category_bar = tqdm.tqdm(total=n_categories, desc="Product Categories", leave=True, position=0)

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

        #page_df = scrape_product_category_data(driver.page_source, next_category_name)
        page_df = scrape_product_category_data(driver=driver, page_source=driver.page_source, category=next_category_name, extract_nutrition=False)
        #page_df = extract_product_data(driver)
        page_dfs.append(page_df)

        if go_next_page(driver) == False:
            break

    while True:
        if go_back(driver) == False:
            break

dfs = pd.concat(page_dfs, ignore_index=True)
dfs.to_csv(output_path)
dfs.reset_index(drop=True, inplace=True)
driver.close()