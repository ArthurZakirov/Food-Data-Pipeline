import pandas as pd
import hydra
from omegaconf import DictConfig
import os
from src.rewe_data.cleaning import clean_rewe_dataset
from src.my_langchain.chain import build_chain_from_config
from src.my_langchain.dataframe_operations import process_df_column_with_llm_in_chunks


@hydra.main(version_base=None, config_path="../../config", config_name="config")
def main(args: DictConfig):
    df = pd.read_csv(args.data.input_path)
    output_df = process_df_column_with_llm_in_chunks(
        chain_config=args.chain,
        df=df,
        input_column=args.data.input_column,
        output_column=args.data.output_column,
        chunk_size=50,
    )
    output_df.to_csv(args.data.output_path, index=False)


if __name__ == "__main__":
    main()
