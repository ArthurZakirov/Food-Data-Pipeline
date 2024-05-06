import requests
import os
import pandas as pd
from tqdm import tqdm


def load_food_dataframe(path: str) -> pd.DataFrame:
    food_df = pd.read_csv(os.path.join(path, "food.csv"))
    food_df = food_df.loc[food_df["data_type"] == "foundation_food"]
    food_df.rename(columns={"description": "FDC Name"}, inplace=True)
    food_df.drop(columns=["data_type", "publication_date"], inplace=True)
    food_df.reset_index(drop=True, inplace=True)
    return food_df


def load_food_category_dataframe(path: str) -> pd.DataFrame:
    food_category_df = pd.read_csv(os.path.join(path, "food_category.csv"))
    food_category_df.rename(
        columns={"description": "Food Category", "id": "food_category_id"}, inplace=True
    )
    food_category_df.drop(columns=["code"], inplace=True)
    return food_category_df


def load_food_nutrient_dataframe(path: str) -> pd.DataFrame:
    food_nutrient_df = pd.read_csv(os.path.join(path, "food_nutrient.csv"))
    food_nutrient_df = food_nutrient_df[["fdc_id", "nutrient_id", "amount"]]
    food_nutrient_df.rename(
        columns={"nutrient_id": "Nutrient ID", "amount": "Nutrient Amount [G]"},
        inplace=True,
    )
    return food_nutrient_df


def load_nutrient_dataframe(path):
    nutrient_df = pd.read_csv(os.path.join(path, "nutrient.csv"))
    VITAMINS = [
        "Vitamin A",
        "Vitamin B-6",
        "Vitamin B-12",
        "Vitamin C",
        "Vitamin D2",
        "Vitamin D3",
        "Vitamin D4",
        "Vitamin E",
        "Vitamin K",
    ]
    ACIDS = ["Thiamin", "Riboflavin", "Niacin", "Folate", "Choline"]
    ELEMENTS = [
        "Phosphorus",
        "Potassium",
        "Sodium",
        "Zinc",
        "Copper",
        "Selenium",
        "Magnesium",
        "Iron",
        "Calcium",
    ]
    FATS = ["fat"]
    CARBS = ["Carbohydrate"]
    PROTEINS = ["Protein"]
    ENERGY = ["Energy"]

    nutrients = []
    nutrients = VITAMINS + ACIDS + ELEMENTS + FATS + CARBS + PROTEINS

    for name in nutrients:
        nutrient_df.loc[nutrient_df["name"].str.contains(name), "name"] = name

    nutrient_df.loc[nutrient_df["name"].isin(PROTEINS), "Category"] = "Macronutrient"
    nutrient_df.loc[nutrient_df["name"].isin(CARBS), "Category"] = "Macronutrient"
    nutrient_df.loc[nutrient_df["name"].isin(FATS), "Category"] = "Macronutrient"
    nutrient_df.loc[nutrient_df["name"].isin(ELEMENTS), "Category"] = "Micronutrient"
    nutrient_df.loc[nutrient_df["name"].isin(ACIDS), "Category"] = "Micronutrient"
    nutrient_df.loc[nutrient_df["name"].isin(VITAMINS), "Category"] = "Micronutrient"
    nutrient_df.dropna(inplace=True)

    nutrient_df.loc[:, "name"] = (
        nutrient_df.loc[:, "name"] + " [" + nutrient_df.loc[:, "unit_name"] + "]"
    )

    nutrient_df = nutrient_df[["id", "name", "Category"]]
    nutrient_df.rename(
        columns={
            "id": "Nutrient ID",
            "name": "Nutrient Name",
            "Category": "Nutrient Category",
        },
        inplace=True,
    )
    return nutrient_df


def rotate_nutrient_rows_to_columns(merged_df):
    merged_df["unique_id"] = merged_df.groupby("FDC Name").cumcount()
    pivot = merged_df.pivot(
        index=["FDC Name", "unique_id"],
        columns=["Nutrient Category", "Nutrient Name"],
        values="Nutrient Amount [G]",
    ).fillna(0)

    pivot = pivot.reset_index(level="unique_id", drop=True)
    pivot = pivot.groupby("FDC Name").sum()
    pivot = pivot.reset_index()

    pivot[("Macronutrient", "Energy [KCAL]")] = (
        pivot[("Macronutrient", "Carbohydrate [G]")] * 4
        + pivot[("Macronutrient", "Protein [G]")] * 4
        + pivot[("Macronutrient", "fat [G]")] * 9
    )

    columns = pivot.columns.tolist()

    new_columns = [
        ("Non Nutrient Data", "FDC Name") if col == ("FDC Name", "") else col
        for col in columns
    ]
    pivot.columns = pd.MultiIndex.from_tuples(new_columns)
    return pivot


def merge_dataframes(food_df, food_category_df, food_nutrient_df, nutrient_df):
    # Initial merging
    merged_df = pd.merge(
        food_df,
        food_category_df,
        on="food_category_id",
        how="inner",
    ).drop(columns=["food_category_id"])

    non_nutrient_df = merged_df.copy()
    non_nutrient_df.columns = pd.MultiIndex.from_tuples(
        [("Non Nutrient Data", col) for col in merged_df.columns]
    )

    # Further merging with food_nutrient_df and nutrient_df
    merged_df = pd.merge(merged_df, food_nutrient_df, on="fdc_id", how="inner").drop(
        columns=["fdc_id"]
    )

    merged_df = pd.merge(merged_df, nutrient_df, on="Nutrient ID", how="inner").drop(
        columns=["Nutrient ID"]
    )

    pivot = rotate_nutrient_rows_to_columns(merged_df)

    pivot = non_nutrient_df.merge(pivot).drop(columns=[("Non Nutrient Data", "fdc_id")])

    pivot = pivot.sort_index(axis=1, level=0)
    return pivot


def query_and_merge_fdc_db(path: str) -> pd.DataFrame:
    food_df = load_food_dataframe(path)
    food_category_df = load_food_category_dataframe(path)
    food_nutrient_df = load_food_nutrient_dataframe(path)
    nutrient_df = load_nutrient_dataframe(path)
    fdc_df = merge_dataframes(food_df, food_category_df, food_nutrient_df, nutrient_df)
    return fdc_df
