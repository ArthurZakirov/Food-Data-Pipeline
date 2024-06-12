import pandas as pd
import re
import json


def parse_price_per_unit(row):
    if pd.notna(row["Amount"]) and pd.notna(row["Price"]):
        price = float(row["Price"].replace("€", "").replace(",", ".").strip())
        amount = float(
            row["Amount"]
        )  # This should already be adjusted to per 100g units
        if amount > 0:
            price_per_unit = price / amount
            return round(price_per_unit, 2)
    return None


def extract_unit_and_amount_from_name(name):
    match = re.search(r"(\d+,\d+|\d+)\s*(kg|g|ml|l)", name)
    if match:
        amount = match.group(1).replace(",", ".")
        unit = match.group(2)
        if unit == "kg":
            unit = "100g"
            amount = float(amount) * 10  # Convert kg to units of 100g
        elif unit == "g":
            unit = "100g"
            amount = float(amount) / 100  # Normalize grams to units of 100g
        elif unit == "l":
            unit = "100g"
            amount = (
                float(amount) * 1000 / 100
            )  # Convert liters to grams and then to units of 100g
        elif unit == "ml":
            unit = "100g"
            amount = float(amount) / 100  # Normalize milliliters to units of 100g
        return unit, amount
    return None, None


def remove_patterns(df):
    patterns_to_remove = [
        r"ja!\s*",
        r"\bca\.\s*",
        r"\bBio\b",
        r"\bREWE\b",
        r"\bBeste Wahl\b",
        r"\bUNSER LAND\b",
        r"\baus der Region\b",
        r"\bim Netz\b",
        r"\bim Beutel\b",
        r"\bim Kochbeutel\b",
        r"\bim Topf\b",
        r"\bim Glas\b",
    ]
    for pattern in patterns_to_remove:
        df["Name"] = df["Name"].apply(
            lambda x: re.sub(pattern, "", x, flags=re.IGNORECASE).strip()
        )
    return df


def drop_unnecessary_data(df):
    categories_to_remove = [
        "Angebote",
        "Grillsaison",
        "Vegane Vielfalt",
        "International",
        "Regional",
        "Weinfreunde",
        "Getränke & Genussmittel",
        "Drogerie & Kosmetik",
        "Babybedarf",
        "Tierbedarf",
        "Küche & Haushalt",
        "Haus & Freizeit",
        "Kaffee, Tee & Kakao",
    ]

    df.dropna(subset=["Grammage"], inplace=True)
    df.dropna(subset=["Name"], inplace=True)
    df["Original Name"] = df["Name"]
    df = df[~df["Category"].isin(categories_to_remove)]
    df.reset_index(drop=True, inplace=True)
    df = df.drop_duplicates(subset=["Original Name"], keep="first")
    return df


def handle_stueck_entries(df, weights_per_stueck_list):
    # Function to remove 'Stück' and associated number from the name
    def clean_name(name):
        return re.sub(r"\d+\s*Stück", "", name).strip()

    # Function to extract 'Stück' and its associated number from Grammage or Name
    def extract_stueck_and_number(text):
        match = re.search(r"(\d+)\s*Stück", text)
        if match:
            return "Stück", match.group(1)
        return None, None

    # Processing each row for missing unit or amount
    for index, row in df.iterrows():
        if row["Unit"] is None or row["Amount"] is None:
            unit, amount = extract_stueck_and_number(row["Name"])
            if unit is None or amount is None:
                unit, amount = extract_stueck_and_number(row["Grammage"])
            df.at[index, "Unit"] = unit if unit is not None else df.at[index, "Unit"]
            df.at[index, "Amount"] = (
                amount if amount is not None else df.at[index, "Amount"]
            )
            if unit == "Stück" and amount is not None:
                df.at[index, "Price per Unit"] = round(
                    float(row["Price"].replace("€", "").replace(",", ".").strip())
                    / float(amount),
                    2,
                )
        # Clean up the name regardless
        df.at[index, "Name"] = clean_name(row["Name"])

    weights_dict = {
        item["Name"]: item["Weight (g)"] for item in weights_per_stueck_list
    }

    df["Weight per Unit (g)"] = df["Name"].apply(
        lambda x: weights_dict.get(x, 100)
    )  # default to 100g if not found
    df["Price per 100g"] = df.apply(
        lambda row: (
            row["Price per Unit"]
            if row["Unit"] == "100g"
            else (row["Price per Unit"] / row["Weight per Unit (g)"]) * 100
        ),
        axis=1,
    )
    return df


def process_price_and_grammage(df):

    # Apply extraction function to the 'Name' column
    unit, amount = zip(*df["Name"].apply(extract_unit_and_amount_from_name))

    df.loc[:, "Unit"] = unit
    df.loc[:, "Amount"] = amount
    # Clean up the 'Name' column
    name = df["Name"].apply(
        lambda x: re.sub(r"\d+,\d+\s*(kg|g|ml|l)|\d+\s*(kg|g|ml|l)", "", x).strip()
    )
    df.loc[:, "Name"] = name

    # If units or amounts are missing, attempt to extract from 'Grammage'
    for index, row in df[df["Unit"].isnull() | df["Amount"].isnull()].iterrows():
        if any(x in row["Grammage"] for x in ["kg", "g", "ml", "l"]):
            unit, amount = extract_unit_and_amount_from_name(row["Grammage"])
            df.at[index, "Unit"] = unit or df.at[index, "Unit"]
            df.at[index, "Amount"] = amount or df.at[index, "Amount"]

    # Calculate the price per unit
    df.loc[:, "Price per Unit"] = df.apply(parse_price_per_unit, axis=1)
    return df


def clean_rewe_dataset(df, weights_list_path):

    with open(weights_list_path, "r") as f:
        weights_per_stueck_list = json.load(f)

    df = drop_unnecessary_data(df)
    df = remove_patterns(df)
    df = process_price_and_grammage(df)
    df = handle_stueck_entries(df, weights_per_stueck_list)
    df.drop(
        columns=[
            "Table Data",
            "Unnamed: 0",
            "Price",
            "Grammage",
            "IsOffer",
            # "Category",
        ],
        inplace=True,
    )
    return df
