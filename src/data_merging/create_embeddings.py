import pandas as pd
import argparse
import os
import dotenv
import hydra
from omegaconf import DictConfig

from src.my_langchain.dataframe_operations import pandas_llm_merge
from src.my_pandas.multi_index import flatten_columns_inplace, unflatten_columns_inplace
from src.my_langchain.embedding import load_csv_retriever

dotenv.load_dotenv()


@hydra.main(version_base=None, config_path="../../config", config_name="config")
def main(args: DictConfig):
    retriever = load_csv_retriever(args.embedding)
    results = retriever.invoke("Cottage cheese")
    print("\n\n\n")
    print(results)


if __name__ == "__main__":
    main()
