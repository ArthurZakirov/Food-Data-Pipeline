import pandas as pd
import argparse
import os
import dotenv
import hydra
from omegaconf import DictConfig

from src.my_langchain.dataframe_operations import pandas_llm_merge
from src.my_pandas.multi_index import flatten_columns_inplace, unflatten_columns_inplace

dotenv.load_dotenv()


@hydra.main(version_base=None, config_path="../../config", config_name="config")
def main(args: DictConfig):

    rewe_df = pd.read_csv(args.data.rewe_path)
    fdc_df = pd.read_csv(args.data.fdc_path)

    n_rows = 50
    rewe_df = rewe_df.loc[:n_rows, :]
    fdc_df = fdc_df.loc[:n_rows, :]

    rewe_df.columns = pd.MultiIndex.from_tuples(
        [("Non Nutrient Data", col) for col in rewe_df.columns]
    )

    rewe_df = flatten_columns_inplace(rewe_df)
    # fdc_df = flatten_columns_inplace(fdc_df)

    print("\n Columns after flattening: \n")
    print(fdc_df.columns)

    print("\n Columns after flattening: \n")
    print(rewe_df.columns)

    merged_df = pandas_llm_merge(
        df_1=rewe_df,
        df_2=fdc_df,
        left_on="Non Nutrient Data.Regulated Name English",
        right_on="Non Nutrient Data.FDC Name",
        chain_config=args.chain,
        chunk_size=20,
    )

    merged_df.to_csv(args.data.output_path, index=False)


if __name__ == "__main__":
    main()
