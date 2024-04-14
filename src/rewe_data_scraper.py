from bs4 import BeautifulSoup
import pandas as pd

# Sample HTML content, replace with your actual HTML content
# html_content = ...

def scrape_product_category_data(product_category):
    soup = BeautifulSoup(product_category, 'html.parser')

    # List to store product dictionaries
    product_list = []

    # Find all products
    products = soup.find_all('div', class_='search-service-product')

    # Extract details for each product and store in a dictionary
    for product in products:
        product_dict = {"Name": None, "Price": None, "Grammage": None, "IsOffer": False}
        
        # Find name
        name_div = product.find('h4', class_='ProductDetailsWrapper_productTitle__XjgsA')
        product_dict["Name"] = name_div.get_text(strip=True) if name_div else "Name not found"

        # Find offer price
        offer_price_div = product.find('div', class_='search-service-productOfferPrice')
        if offer_price_div:
            product_dict["Price"] = offer_price_div.get_text(strip=True)
            product_dict["IsOffer"] = True
        else:
            # Find regular price if offer price not found
            regular_price_div = product.find('div', class_='search-service-productPrice')
            if regular_price_div:
                product_dict["Price"] = regular_price_div.get_text(strip=True)
        
        # Find grammage
        grammage_div = product.find('div', class_='ProductGrammage_productGrammage__fMOJr')
        product_dict["Grammage"] = grammage_div.get_text(strip=True) if grammage_div else "Grammage not found"
        
        # Add the product dictionary to the list
        product_list.append(product_dict)

    # Create DataFrame
    df = pd.DataFrame(product_list)
    return df
