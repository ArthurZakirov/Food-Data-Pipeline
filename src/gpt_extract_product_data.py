import pandas as pd
import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_product_data(driver, product, extract_nutrition=False, waiting_time=0.1):
    product_dict = {"Name": None, "Price": None, "Grammage": None, "IsOffer": False, "Category": None, "Table Data": None}

    # Extracting surface data from BeautifulSoup element
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

    # Extracting nutritional data if option is enabled
    if extract_nutrition:
        link = product.find('a', class_='search-service-productDetailsLink')['href']
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
                cells = row.find_elements(By.TAG_NAME, "td")
                cell_texts = [cell.text.replace('\n', ' ').replace('\r', '') for cell in cells]
                table_data_string += ",".join(cell_texts) + "\n"
            product_dict["Table Data"] = table_data_string
        except:
            product_dict["Table Data"] = "No nutritional data found"

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return product_dict

def scrape_product_category_data(driver, page_source, category, extract_nutrition=False):
    soup = BeautifulSoup(page_source, 'html.parser')
    products = soup.find_all('div', class_='search-service-product')
    product_dicts = []

    for product in tqdm.tqdm(products, desc="Processing Products", leave=False):
        product_info = extract_product_data(driver, product, extract_nutrition, waiting_time=0.1)
        product_info["Category"] = category
        product_dicts.append(product_info)

    df = pd.DataFrame(product_dicts)
    return df
