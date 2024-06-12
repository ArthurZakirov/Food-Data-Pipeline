import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import tqdm


def random_sleep(min_sec=1, max_sec=5):
    """Sleep for a random amount of time between min_sec and max_sec."""
    time.sleep(random.uniform(min_sec, max_sec))


def go_to_next_category(driver, visited_category_names):

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "home-page-category-tile"))
    )
    categories = driver.find_elements(By.CLASS_NAME, "home-page-category-tile")

    for category in categories:
        name = category.accessible_name
        if name not in visited_category_names:
            driver.execute_script("arguments[0].click();", category)
            return name
    return False


def go_next_page(driver):
    # Wait for any potential clickable navigation arrow to be present.
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".PaginationArrow_paginationArrowEnabled___He_R")
        )
    )

    # Find all elements that could potentially be navigation arrows.
    arrows = driver.find_elements(
        By.CSS_SELECTOR, ".PaginationArrow_paginationArrowEnabled___He_R"
    )
    for arrow in arrows:
        if arrow.accessible_name == ">" and "Disabled" not in arrow.get_attribute(
            "class"
        ):
            driver.execute_script("arguments[0].click();", arrow)
            return True

    return False


def go_back(driver):
    try:
        # Wait for the element to be present.
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, "breadcrumbLink0"))
        )
        buttons = driver.find_elements(By.ID, "breadcrumbLink0")

        # Check for the accessible name "Zurück" and click if found.
        for button in buttons:
            if button.accessible_name == "Zurück":
                driver.execute_script("arguments[0].click();", button)
                return True

    except TimeoutException:
        # Handle the case where the element isn't found within the timeout.
        pass

    # Return False if the button wasn't found or clicked.
    return False


def go_back_from_product(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "lr-breadcrumbs__link"))
    )
    buttons = driver.find_elements(By.CLASS_NAME, "lr-breadcrumbs__link")
    back_button = buttons[0]
    driver.execute_script("arguments[0].click();", back_button)
    return True


def get_number_of_product_categories(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "home-page-category-tile"))
    )
    return len(driver.find_elements(By.CLASS_NAME, "home-page-category-tile"))


def get_number_of_pages(driver):
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "Pagination_paginationPagesContainer__b2Lv_")
        )
    )

    buttons = container.find_elements(By.TAG_NAME, "button")
    num_pages = int(buttons[-1].accessible_name)
    return num_pages

    # for i, button in enumerate(buttons):
    #     if button.accessible_name == ">":
    #         num_pages = int(buttons[i - 1].accessible_name)
    #         return num_pages
    # return 1
