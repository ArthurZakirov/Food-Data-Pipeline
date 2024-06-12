import requests
import os
import pandas as pd
from tqdm import tqdm


def load_food_dataframe(path: str) -> pd.DataFrame:
    food_df = pd.read_csv(os.path.join(path, "food.csv"))
    # food_df = food_df.loc[food_df["data_type"] == "foundation_food"]
    food_df = food_df.loc[food_df["data_type"] == "sr_legacy_food"]

    food_df = food_df.drop_duplicates(subset="description", keep="first")
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
    food_nutrient_df["Nutrient Amount [G]"] = food_nutrient_df[
        "Nutrient Amount [G]"
    ].clip(lower=0)
    return food_nutrient_df


def load_nutrient_dataframe(path):
    # Load the nutrient data from a CSV file
    nutrient_df = pd.read_csv(os.path.join(path, "nutrient.csv"))

    # Lookup table for standardizing names with regex patterns
    lookup_table = {
        "Vitamin A": ["Vitamin A, RAE", r"Vitamin A, RAE.*"],
        "Vitamin B-6": ["Vitamin B-6", r"Vitamin B-6.*"],
        "Vitamin B-12": ["Vitamin B-12", r"Vitamin B-12.*"],
        "Vitamin C": ["Vitamin C", r"Vitamin C.*"],
        # "Vitamin D2": ["Vitamin D2", r"Vitamin D2.*"],
        # "Vitamin D3": ["Vitamin D3", r"Vitamin D3.*"],
        "Vitamin D4": ["Vitamin D4", r"Vitamin D4.*"],
        "Vitamin E": ["Vitamin E", r"Vitamin E.*"],
        "Vitamin K1": ["Vitamin K \(phylloquinone\)"],
        "Vitamin K2": ["Vitamin K \(Menaquinone-4\)"],
        "Thiamin": ["Thiamin", r"Thiamin.*"],
        "Riboflavin": ["Riboflavin", r"Riboflavin.*"],
        "Niacin": ["Niacin", r"Niacin.*"],
        "Folate": ["Folate, total", r"Folate, total.*"],
        "Choline": ["Choline", r"Choline.*"],
        "Phosphorus": ["Phosphorus", r"Phosphorus.*"],
        "Potassium": ["Potassium", r"Potassium.*"],
        "Sodium": ["Sodium", r"Sodium.*"],
        "Iodine": ["Iodine", r"Iodine.*"],
        "Zinc": ["Zinc", r"Zinc.*"],
        "Copper": ["Copper", r"Copper.*"],
        "Selenium": ["Selenium", r"Selenium.*"],
        "Magnesium": ["Magnesium", r"Magnesium.*"],
        "Manganese": ["Manganese", r"Manganese.*"],
        "Chromium": ["Chromium", r"Chromium.*"],
        "Molybdenum": ["Molybdenum", r"Molybdenum.*"],
        "Biotin": ["Biotin", r"Biotin.*"],
        "Iron": ["Iron", r"Iron.*"],
        "Calcium": ["Calcium", r"Calcium.*"],
        "Total Fat": [r"(?i)^((?!fatty acids).)*total.*fat.*$"],
        "Carbohydrate": ["Carbohydrate", r"Carbohydrates.*"],
        "Protein": ["Protein", r"Protein.*"],
        "Fiber": [r"(?i).*total.*fiber.*|.*fiber.*total.*"],
        "Saturated Fat": [
            r"^(?!.*(?:polyunsat|monounsat)).*Fatty acids,.*(saturated|sat\.).*"
        ],
        "Sugars, added": ["Sugars, added", r"Sugars, added.*"],
        # "Omega 3": [r"(EPA|DHA)"],
        "Omega 3 (EPA)": ["EPA"],
        "Omega 3 (DHA)": ["DHA"],
        "Omega 3 (ALA)": ["ALA"],
        "Omega 6": [r"(18:2 n-6|18:3 n-6|20:4 n-6)"],
        # "Omega 6 (LA)": ["18:2 n-6"],
        # "Omega 6 (GLA)": ["18:3 n-6"],
        # "Omega 6 (AA)": ["20:4 n-6"],
        # "Total Sugars": [r"(?i).*total.*sugars.*|.*sugars.*total.*"],
    }

    # Apply each pattern and update the 'name' column
    for standard_name, patterns in lookup_table.items():
        pattern_regex = "|".join(
            patterns
        )  # Combine all patterns for this name into one regex
        nutrient_df.loc[
            nutrient_df["name"].str.contains(pattern_regex, case=False, regex=True),
            "name",
        ] = standard_name

    # Define categories based on the final standardized names
    macro_categories = [
        "Total Fat",
        "Saturated Fat",
        "Carbohydrate",
        "Protein",
        "Fiber",
        # "Total Sugars",
        "Sugars, added",
    ]
    micro_categories = list(set(lookup_table.keys()) - set(macro_categories))

    nutrient_df.loc[nutrient_df["name"].isin(micro_categories), "Category"] = (
        "Micronutrient"
    )
    nutrient_df.loc[nutrient_df["name"].isin(macro_categories), "Category"] = (
        "Macronutrient"
    )
    nutrient_df.dropna(inplace=True)

    # Simplify the DataFrame to select useful columns and rename them
    nutrient_df = nutrient_df[~(nutrient_df["unit_name"] == "kJ")]
    nutrient_df = nutrient_df[~(nutrient_df["unit_name"] == "KCAL")]

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

    # def custom_agg(sub_df):
    #     # Here, sub_df is the DataFrame group passed by apply()
    #     if (
    #         sub_df["Nutrient Name"].iloc[0] == "Omega 3"
    #         or sub_df["Nutrient Name"].iloc[0] == "Omega 6"
    #     ):
    #         return sub_df[
    #             "Nutrient Amount [G]"
    #         ].sum()  # Sum if the nutrient name is "Omega 3"
    #     else:
    #         return sub_df["Nutrient Amount [G]"].mean()

    grouped = (
        merged_df.groupby(["FDC Name", "Nutrient Category", "Nutrient Name"])
        .agg({"Nutrient Amount [G]": "mean"})
        .reset_index()
    )

    # grouped = (
    #     merged_df.groupby(["FDC Name", "Nutrient Category", "Nutrient Name"])
    #     .apply(custom_agg)
    #     .reset_index()
    # )

    # Now pivot this aggregated data
    pivot = grouped.pivot(
        index="FDC Name",
        columns=["Nutrient Category", "Nutrient Name"],
        values="Nutrient Amount [G]",
    ).fillna(0)

    # Finally, reset the index to make 'FDC Name' a column again
    pivot = pivot.reset_index()

    pivot[("Energy", "Energy [KCAL]")] = (
        pivot[("Macronutrient", "Carbohydrate [G]")] * 4
        + pivot[("Macronutrient", "Protein [G]")] * 4
        + pivot[("Macronutrient", "Total Fat [G]")] * 9
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


def clean_fdc_data(df):
    df[("Micronutrient", "Omega 3 (EPA + DHA) [G]")] = (
        df[("Micronutrient", "Omega 3 (EPA) [G]")]
        + df[("Micronutrient", "Omega 3 (DHA) [G]")]
    )
    df.drop(
        columns=[
            ("Micronutrient", "Omega 3 (EPA) [G]"),
            ("Micronutrient", "Omega 3 (DHA) [G]"),
        ],
        inplace=True,
    )
    df[("Micronutrient", "Vitamin K [UG]")] = (
        df[("Micronutrient", "Vitamin K1 [UG]")]
        + df[("Micronutrient", "Vitamin K2 [UG]")]
    )
    df.drop(
        columns=[
            ("Micronutrient", "Vitamin K1 [UG]"),
            ("Micronutrient", "Vitamin K2 [UG]"),
        ],
        inplace=True,
    )
    df = df[
        ~df[("Non Nutrient Data", "Food Category")].isin(
            ["Sweets", "Soups, Sauces, and Gravies", "Beverages", "Baby Foods"]
        )
    ]
    df = df[~df[("Non Nutrient Data", "FDC Name")].str.contains("Flour")]
    df = df[~df[("Non Nutrient Data", "FDC Name")].str.contains("added vitamin")]
    df = df[["Non Nutrient Data", "Energy", "Macronutrient", "Micronutrient"]]
    return df


def query_and_merge_fdc_db(path: str) -> pd.DataFrame:
    food_df = load_food_dataframe(path)
    food_category_df = load_food_category_dataframe(path)
    food_nutrient_df = load_food_nutrient_dataframe(path)
    nutrient_df = load_nutrient_dataframe(path)
    df = merge_dataframes(food_df, food_category_df, food_nutrient_df, nutrient_df)
    df = clean_fdc_data(df)
    return df
