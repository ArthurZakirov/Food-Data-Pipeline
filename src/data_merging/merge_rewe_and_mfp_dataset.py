from src.myfitnesspal.client import load_myfitnesspal_client
from src.data_merging.mfp_merger import fetch_nutrients_from_myfitnesspal

import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    "--rewe_data_path",
    type=str,
    default="data/processed/cleaned_rewe_dataset.csv",
)
parser.add_argument(
    "--output_path", type=str, default="data/processed/merged_rewe_mfp_dataset.csv"
)

args = parser.parse_args()


def main():
    df = pd.read_csv(args.rewe_data_path)

    client = load_myfitnesspal_client()
    nutrients_df = fetch_nutrients_from_myfitnesspal(df, client)
    nutrients_df.to_csv(args.output_path, index=False)


if __name__ == "__main__":
    main()
