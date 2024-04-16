import time
import sys
import json
import tqdm 
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


def random_sleep(min_sec=1, max_sec=5):
    """Sleep for a random amount of time between min_sec and max_sec."""
    time.sleep(random.uniform(min_sec, max_sec))

def scrape_product_category_data(page_source, category):
    soup = BeautifulSoup(page_source, 'html.parser')
    product_list = []
    products = soup.find_all('div', class_='search-service-product')

    product_bar = tqdm.tqdm(products, desc="Products On Page", total=len(products), leave=False, position=2, file=sys.stdout)

    for product in products:

        product_dict = {"Name": None, "Price": None, "Grammage": None, "IsOffer": False, "Category": category}

        name_div = product.find('h4', class_='ProductDetailsWrapper_productTitle__XjgsA')
        product_dict["Name"] = name_div.get_text(strip=True) if name_div else "Name not found"

        offer_price_div = product.find('div', class_='search-service-productOfferPrice')
        if offer_price_div:
            product_dict["Price"] = offer_price_div.get_text(strip=True)
            product_dict["IsOffer"] = True
        else:
            regular_price_div = product.find('div', class_='search-service-productPrice')
            if regular_price_div:
                product_dict["Price"] = regular_price_div.get_text(strip=True)
        
        grammage_div = product.find('div', class_='ProductGrammage_productGrammage__fMOJr')
        product_dict["Grammage"] = grammage_div.get_text(strip=True) if grammage_div else "Grammage not found"

        product_list.append(product_dict)
        product_bar.update(1)

    df = pd.DataFrame(product_list)
    return df

def load_driver(config_path):
    with open(config_path, "r") as f:
        edge_options_dict = json.load(f)
        
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_experimental_option("debuggerAddress", f"localhost:{edge_options_dict['remote-debugging-port']}")

    service = Service(edge_options_dict["edge_driver_path"])
    driver = webdriver.Edge(service=service, options=edge_options)
    driver.get(f"{edge_options_dict['rewe_url']}")
    return driver

def go_to_next_category(driver, visited_category_names):
    categories = driver.find_elements(By.CLASS_NAME, "home-page-category-tile")
    for category in categories:
        name = category.accessible_name
        if name not in visited_category_names:
            driver.execute_script("arguments[0].click();", category)
            return name
    return False


def go_next_page(driver):
    buttons = driver.find_elements(By.TAG_NAME, 'button')
    for button in buttons:
        if button.accessible_name == ">" and "Disabled" not in button.get_attribute("class"):
            driver.execute_script("arguments[0].click();", button)
            return True
    return False
    

def go_back(driver):
    buttons = driver.find_elements(By.ID, 'breadcrumbLink0')
    back_button = None
    for button in buttons:
        if button.accessible_name == "Zurück":
            back_button = button
            driver.execute_script("arguments[0].click();", back_button)
            return True
    return False

def go_back_from_product(driver):
    buttons = driver.find_elements(By.CLASS_NAME, 'lr-breadcrumbs__link')
    back_button = buttons[0]
    driver.execute_script("arguments[0].click();", back_button)
    return True
 

def get_number_of_product_categories(driver):
    return len(driver.find_elements(By.CLASS_NAME, "home-page-category-tile"))

def get_number_of_pages(driver):
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for i, button in enumerate(buttons):
        if button.accessible_name == ">":
            num_pages = int(buttons[i - 1].accessible_name)
            return num_pages
    return 1

def extract_product_data(driver, waiting_time=0.1):
    product_dicts = []
    products = driver.find_elements(By.CLASS_NAME, 'search-service-product')

    for i in range(len(products)):
        # Re-query the product list to avoid stale elements
        main_window = driver.current_window_handle
        
        product = products[i]
        product_dict = {"Name": product.accessible_name, "Table Data": None}

        link = product.find_element(By.CLASS_NAME, 'search-service-productDetailsLink')
        
        driver.execute_script("window.open(arguments[0]);", link.get_attribute('href'))
        # Switch to new tab
        driver.switch_to.window(driver.window_handles[1])

        print("Switched window")

        nahrwerte_title_exists = driver.execute_script(
            "return Array.from(document.querySelectorAll('h2')).some(h2 => h2.textContent.includes('Nährwerte'));"
        )

        if nahrwerte_title_exists:
            print("'Nährwerte' title exists. Proceeding to examine the table.")
            nahrwerte_tab = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Nährwerte')]"))
            )

            # Scroll to the Nährwerte tab
            driver.execute_script("arguments[0].scrollIntoView();", nahrwerte_tab)

            # Click the Nährwerte tab
            nahrwerte_tab.click()


            # Waiting for the table to be visible before interacting with it
            nutrition_table = WebDriverWait(driver, waiting_time).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "pdpr-NutritionTable"))
            )


            # Now you can extract the data from the table
            rows = nutrition_table.find_elements(By.TAG_NAME, "tr")
            table_data_string = ""
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                cell_texts = [cell.text.replace('\n', ' ').replace('\r', '') for cell in cells]
                table_data_string += ",".join(cell_texts) + "\n"

            
        else:
            table_data_string = ""

        print(table_data_string)
        product_dict["Table Data"] = table_data_string
        product_dicts.append(product_dict)

        go_back_from_product(driver)

        driver.close()
        driver.switch_to.window(main_window)

    df = pd.DataFrame(product_dicts)
    return df
