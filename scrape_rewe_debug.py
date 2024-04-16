import os
import sys
import pandas as pd
import tqdm
from selenium.webdriver.common.by import By

sys.path.append("..")
#os.chdir(os.path.join(os.getcwd(), ".."))

from src.rewe_data_scraper import load_driver, go_to_next_category, scrape_product_category_data, go_next_page, go_back
from src.rewe_data_scraper import get_number_of_product_categories, get_number_of_pages, random_sleep, go_back_from_product

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

output_path = "data/rewe_dataset.csv"
driver = load_driver(config_path="config/rewe_browser_config.json")

visited_category_names = []
page_dfs = []
n_categories = get_number_of_product_categories(driver)

random_sleep(0, 1)

driver.get("https://shop.rewe.de/p/leicht-cross-knusperbrot-vollkorn-125g/826936")

go_back_from_product(driver)
