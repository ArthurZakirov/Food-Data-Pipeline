import argparse
import pandas as pd
from src.food_data_central.loader import query_and_merge_fdc_db

parser = argparse.ArgumentParser()
parser.add_argument(
    "--raw_data_path",
    type=str,
    default="data/raw/FoodData_Central_sr_legacy_food_csv_2018-04",
    # "data/raw/FoodData_Central_foundation_food_csv_2024-04-18"
)
parser.add_argument("--output_path", type=str, default="data/processed/fdc_data.h5")

args = parser.parse_args()


def main():
    df = query_and_merge_fdc_db(args.raw_data_path)
    df.to_hdf(args.output_path, key="nutrition", mode="w")


if __name__ == "__main__":
    main()
