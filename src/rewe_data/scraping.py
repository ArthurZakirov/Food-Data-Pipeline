import time
import sys
import json
import random
import pandas as pd
import tqdm
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_product_data(product):
    product_dict = {
        "Name": None,
        "Price": None,
        "Grammage": None,
        "IsOffer": False,
        "Category": None,
        "Table Data": None,
    }

    # Extracting surface data from BeautifulSoup element
    name_div = product.find("h4", class_="ProductDetailsWrapper_productTitle__XjgsA")
    product_dict["Name"] = (
        name_div.get_text(strip=True) if name_div else "Name not found"
    )

    offer_price_div = product.find("div", class_="search-service-productOfferPrice")
    if offer_price_div:
        product_dict["Price"] = offer_price_div.get_text(strip=True)
        product_dict["IsOffer"] = True
    else:
        regular_price_div = product.find("div", class_="search-service-productPrice")
        if regular_price_div:
            product_dict["Price"] = regular_price_div.get_text(strip=True)

    grammage_div = product.find("div", class_="ProductGrammage_productGrammage__fMOJr")
    product_dict["Grammage"] = (
        grammage_div.get_text(strip=True) if grammage_div else "Grammage not found"
    )

    return product_dict


from selenium.common.exceptions import TimeoutException, NoSuchElementException


def extract_regulated_product_name_from_product(product, driver, waiting_time=0.1):

    href = product.find("a", class_="search-service-productDetailsLink")["href"]
    href_full = (
        f"https://shop.rewe.de{href}"  # Assuming the base URL needs to be appended
    )

    # Use Selenium to find and click the link with the specific href
    xpath = f"//a[@href='{href}']"  # Construct an XPath to find the link by its href attribute
    product_link = WebDriverWait(driver, waiting_time).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    product_link.click()  # Click the link

    # Wait for the new page to load and extract the regulated product name
    try:
        WebDriverWait(driver, waiting_time).until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, "pdpr-RegulatedProductName")
            )
        )
        regulated_product_name_element = driver.find_element(
            By.CLASS_NAME, "pdpr-RegulatedProductName"
        )
        regulated_product_name = regulated_product_name_element.text
    except (TimeoutException, NoSuchElementException):
        regulated_product_name = ""
    driver.back()
    return regulated_product_name


def extract_nutritional_data_from_product(product, driver, waiting_time=1):
    link = product.find("a", class_="search-service-productDetailsLink")["href"]
    driver.execute_script("window.open(arguments[0]);", link)
    driver.switch_to.window(driver.window_handles[-1])

    try:

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Nährwerte')]"))
        )
        nutrition_table = WebDriverWait(driver, waiting_time).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "pdpr-NutritionTable"))
        )
        rows = nutrition_table.find_elements(By.TAG_NAME, "tr")
        table_data_string = ""
        for row in rows:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "td"))
            )
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_texts = [
                cell.text.replace("\n", " ").replace("\r", "") for cell in cells
            ]
            table_data_string += ",".join(cell_texts) + "\n"
            table_data_string
    except:
        table_data_string = "No nutritional data found"

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return table_data_string


def extract_image_url(product):
    """
    Extracts and returns the image URL from a product BeautifulSoup object.

    Args:
    product (bs4.element.Tag): A BeautifulSoup object representing a product.

    Returns:
    str: The URL of the product image.
    """
    # Attempt to find the <img> tag within the product
    img_tag = product.find("img")
    if img_tag and "src" in img_tag.attrs:
        return img_tag["src"]
    else:
        return None


def scrape_product_category_data_from_page(
    driver,
    page_source,
    category,
    extract_regulated_product_name=False,
    extract_nutrition=False,
):
    try:
        # Explicit wait for the products to load
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-service-product"))
        )
    finally:
        # Now retrieve the page source
        soup = BeautifulSoup(driver.page_source, "html.parser")

    product_dicts = []
    products = soup.find_all("div", class_="search-service-product")

    for product in tqdm.tqdm(products, desc="Processing Products", leave=False):
        product_info = extract_product_data(product)
        image_url = extract_image_url(product)
        product_info["Image URL"] = image_url

        if extract_regulated_product_name:
            regulated_product_name = extract_regulated_product_name_from_product(
                product, driver, waiting_time=0.1
            )
            product_info["Regulated Product Name"] = regulated_product_name
        if extract_nutrition:
            nutritional_data = extract_nutritional_data_from_product(
                product, driver, waiting_time=0.1
            )
            product_info["Nutritional Data"] = nutritional_data

        product_info["Category"] = category
        product_dicts.append(product_info)

    df = pd.DataFrame(product_dicts)
    return df
