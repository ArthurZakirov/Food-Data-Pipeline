from src.rewe_data.cleaning import clean_rewe_dataset

import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    "--raw_data_path",
    type=str,
    default="data/raw/rewe_dataset.csv",
)
parser.add_argument(
    "--weights_list_path",
    type=str,
    default="data/raw/rewe_weights_per_stueck_list.json",
)
parser.add_argument(
    "--output_path", type=str, default="data/processed/cleaned_rewe_dataset.csv"
)
args = parser.parse_args()


def main():
    df = pd.read_csv(args.raw_data_path)
    df = clean_rewe_dataset(df, args.weights_list_path)

    print(f"\n\n\nSaving cleaned dataset to {args.output_path}")
    df.to_csv(args.output_path, index=False)


if __name__ == "__main__":
    main()
