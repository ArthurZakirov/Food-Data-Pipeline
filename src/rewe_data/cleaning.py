def parse_price_per_kg(row):
    grammage = row["Grammage"]
    price = row["Price"]
    # If the unit is 'kg' and there is no separate price provided, the price is per kg
    if "kg" in grammage and "=" not in grammage:
        return float(price.split("€")[0].strip().replace(",", ".")) / 10
    elif "kg" in grammage:
        try:
            # If a separate price is provided, extract and convert it to float
            return (
                float(grammage.split("=")[1].split("€")[0].strip().replace(",", "."))
                / 10
            )
        except (IndexError, ValueError):
            return None
    else:
        # If the unit is not 'kg', return None
        return None


def clean_rewe_dataset(df):
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

    df = df[~df["Category"].isin(categories_to_remove)]
    df = df[~df["Grammage"].str.contains("l|Stück")]

    df["Price (EUR/ 100g)"] = df.apply(parse_price_per_kg, axis=1).astype(float)

    df.drop(
        columns=["Price", "Grammage", "IsOffer", "Category", "Table Data"], inplace=True
    )
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
