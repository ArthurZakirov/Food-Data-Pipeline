import pandas as pd
import hydra
from omegaconf import DictConfig
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
    output_df.drop_duplicates(
        subset=args.data.output_column, keep="first", inplace=True
    )
    output_df.to_csv(args.data.output_path, index=False)


if __name__ == "__main__":
    main()
