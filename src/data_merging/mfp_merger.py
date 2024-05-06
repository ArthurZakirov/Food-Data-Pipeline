import pandas as pd
from tqdm import tqdm


def adjust_nutritional_stats(food_data):
    # Define plausible limits for nutritional stats per 100g
    plausible_limits = {}

    # Attempt to access serving size information
    inverse_adjustment_factor = food_data._serving_sizes[0]["nutrition_multiplier"]

    # Set plausible limits for specific nutritional stats
    plausible_limits_keys = ["energy", "fat", "protein", "carbohydrate"]
    for key, value in food_data.details.items():
        for limit_key in plausible_limits_keys:
            if limit_key in key:
                if limit_key == "energy":
                    plausible_limits[key] = (0, 900)
                else:
                    plausible_limits[key] = (0, 100)
                break

    # If gram weight is not 100g, adjust all values accordingly
    if inverse_adjustment_factor != 1:
        for key, value in food_data.details.items():
            if key in plausible_limits:
                food_data.details[key] /= inverse_adjustment_factor

    # Check if the nutritional stats are within plausible limits
    for key, value in food_data.details.items():
        if key in plausible_limits:
            if not (plausible_limits[key][0] <= value <= plausible_limits[key][1]):
                print(f"Invalid value for {key}: {value}")
                return False  # Invalid nutritional stats

    return True  # Nutritional stats are valid


def fetch_nutrients_from_myfitnesspal(df, client):
    df = df.copy()

    for index, row in tqdm(
        df.iterrows(), total=df.shape[0], desc="Fetching food data from MyFitnessPal"
    ):
        name = row["Name"]
        food_search_results = client.get_food_search_results(name)

        for food in food_search_results:
            try:
                food_data = client.get_food_item_details(food.mfp_id)
                food_data.details["energy"] = food_data.details["energy"]["value"]

                if adjust_nutritional_stats(food_data):
                    food_dict = food_data.details.copy()
                    food_dict["energy (kcal)"] = food._calories
                    food_dict["Search Result Name"] = food._name
                    food_dict["Search Result Brand"] = food._brand

                    for key, value in food_dict.items():
                        if key not in df.columns:
                            df[key] = None  # Initialize column if it doesn't exist
                        df.at[index, key] = value
                    break  # Break the loop if valid nutritional stats found
            except Exception as e:
                print(f"An error occurred: {e}")

    return df
