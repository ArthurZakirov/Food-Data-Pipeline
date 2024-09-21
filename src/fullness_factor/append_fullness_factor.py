import pandas as pd
import argument_parser 

parser = argument_parser.ArgumentParser()
parser.add_argument(
    "--data_path",
    type=str,
    default="../data/processed/merged_rewe_fdc_data.csv",
)

args = parser.parse_args()

def calculate_fullness_factor(row):
    CAL = max(30, row['Energy.Energy [KCAL]'])  # Minimum 30
    PR = min(30, row['Macronutrient.Protein [G]'])  # Maximum 30
    DF = min(12, row['Macronutrient.Fiber [G]'])  # Maximum 12
    TF = min(50, row['Macronutrient.Total Fat [G]'])  # Maximum 50
    
    # Fullness Factor formula
    FF = max(0.0, min(5.0, 41.7 / (CAL**0.7) + 0.05 * PR + 6.17e-4 * (DF**3) - 7.25e-6 * (TF**3) + 0.617))
    return FF

def main(args):
    df = pd.read_csv(args.data_path)
    df["Non Nutrient Data.Fullness Factor"] = df.apply(calculate_fullness_factor, axis=1)
    df.to_csv(args.data_path, index=False)

if __name__ == '__main__':
    main(args)
