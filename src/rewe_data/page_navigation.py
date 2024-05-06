import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tqdm


def random_sleep(min_sec=1, max_sec=5):
    """Sleep for a random amount of time between min_sec and max_sec."""
    time.sleep(random.uniform(min_sec, max_sec))


def go_to_next_category(driver, visited_category_names):
    categories = driver.find_elements(By.CLASS_NAME, "home-page-category-tile")
    for category in categories:
        name = category.accessible_name
        if name not in visited_category_names:
            driver.execute_script("arguments[0].click();", category)
            return name
    return False


def go_next_page(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "button"))
    )
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        if button.accessible_name == ">" and "Disabled" not in button.get_attribute(
            "class"
        ):
            driver.execute_script("arguments[0].click();", button)
            return True
    return False


def go_back(driver):
    buttons = driver.find_elements(By.ID, "breadcrumbLink0")
    back_button = None
    for button in buttons:
        if button.accessible_name == "Zurück":
            back_button = button
            driver.execute_script("arguments[0].click();", back_button)
            return True
    return False


def go_back_from_product(driver):
    buttons = driver.find_elements(By.CLASS_NAME, "lr-breadcrumbs__link")
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
