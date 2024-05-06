import pandas as pd
import os
import requests
from tqdm import tqdm


def fetch_nutrients_from_food_data_central(df):

    food_dict_list = []
    for index, row in tqdm(
        df.iterrows(),
        total=df.shape[0],
        desc="Fetching food data from FoodData Central",
    ):
        name = row["Translated Name"]
        params = {
            "api_key": os.environ.get("FOOD_DATA_CENTRAL_API_KEY"),
            "query": name,
            "dataType": ["Foundation"],
            "pageSize": 10,
        }

        response = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search", params=params
        )

        data = response.json()

        food_dict = {}

        if data["totalHits"] > 0:
            # Get the FDC ID of the first result
            food_data = data["foods"][0]

            food_dict["Name"] = name
            food_dict["Search Result Name"] = food_data["description"]
            food_dict["fdc_id"] = food_data["fdcId"]
            food_dict["Category"] = food_data["foodCategory"]

            food_dict_list.append(food_dict)
        else:
            print("No results found")

    food_df = pd.DataFrame(food_dict_list)
    return food_df
