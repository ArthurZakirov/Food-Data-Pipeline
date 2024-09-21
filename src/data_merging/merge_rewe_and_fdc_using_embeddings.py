import argparse
import pandas as pd
import pandas as pd
import chromadb
from tqdm import tqdm

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from scipy.spatial.distance import cdist

parser = argparse.ArgumentParser()
parser.add_argument("--similarity_threshold", type=float, default=0.5)
parser.add_argument("--chroma_path", type=str, default="data/processed/chroma.db")
parser.add_argument("--collection1_name", type=str, default="rewe_data")
parser.add_argument("--collection2_name", type=str, default="fdc_data")
parser.add_argument(
    "--df1_path",
    type=str,
    default="data/processed/cleaned_rewe_dataset_with_extracted_names.csv",
)
parser.add_argument("--df2_path", type=str, default="data/processed/fdc_data.csv")
parser.add_argument(
    "--column1", type=str, default="Non Nutrient Data.Regulated Name English"
)
parser.add_argument("--column2", type=str, default="Non Nutrient Data.FDC Name")
parser.add_argument("--left_on", type=str, default="document_id")
parser.add_argument("--similarity_column_name", type=str, default="similarity")
parser.add_argument(
    "--output_path", type=str, default="data/processed/merge_rewe_fdc_50_percent.csv"
)
args = parser.parse_args()


def load_chroma_collection(client_path, collection_name):
    chroma = chromadb.PersistentClient(path=client_path)
    collection = chroma.get_collection(collection_name)

    documents = collection.get(include=["embeddings", "metadatas", "documents"])
    embeddings = documents["embeddings"]
    metadatas = documents["metadatas"]
    doc_ids = documents["documents"]

    df = pd.DataFrame(metadatas)
    df["embedding"] = embeddings
    df["document_id"] = doc_ids
    df.drop(columns=[0], inplace=True)
    df.drop_duplicates(subset=["document_id"], keep="first", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def merge_embeddings_on_similarity(df1, df2, similarity_column_name="similarity"):
    """
    Merges two dataframes based on the similarity of their embeddings.
    The function computes the cosine similarity between the embeddings of each row in df1 and df2.
    The row in df2 with the highest similarity to the row in df1 is merged with the row in df1.

    - All rows from df1 remain in the merged df.
    - Only the highest similarity rows from df2 are contained in the merged df

    In my specific case:
    - All rows from the REWE dataset are retained in the merged df.
    - Only the highest similarity rows from the FDC dataset are retained in the merged df.
    """

    # Resetting indices to ensure they are sequential
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)

    embeddings1 = np.stack(df1["embedding"].values)
    embeddings2 = np.stack(df2["embedding"].values)

    # Compute the similarity matrix
    similarity_matrix = 1 - cdist(embeddings1, embeddings2, metric="cosine")

    closest_matches = []
    for i, row1 in tqdm(df1.iterrows()):
        if i < similarity_matrix.shape[0]:  # Ensuring the index is within bounds
            best_match_idx = np.argmax(similarity_matrix[i])
            best_similarity = similarity_matrix[i][
                best_match_idx
            ]  # Ensure correct indexing
            row2 = df2.iloc[best_match_idx].to_dict()
            merged_row = {
                **row1.to_dict(),
                **{f"{k}_2": v for k, v in row2.items()},
                similarity_column_name: best_similarity,
            }
            closest_matches.append(merged_row)
        else:
            pass
    merged_df = pd.DataFrame(closest_matches)
    return merged_df


def main(args):
    print("\nLoading data...")

    collection_df1 = load_chroma_collection(args.chroma_path, args.collection1_name)
    print("\nLoaded data from collection 1")

    collection_df2 = load_chroma_collection(args.chroma_path, args.collection2_name)
    print("\nLoaded data from collection 2")

    print("\nCompute similarity and merge data...")
    merged_collections = merge_embeddings_on_similarity(collection_df1, collection_df2)
    print("\nSuccessfully computed similarity")

    df1 = pd.read_csv(args.df1_path)
    df1 = pd.read_csv(args.df1_path)
    df1.columns = ["Non Nutrient Data." + col for col in df1.columns]

    df2 = pd.read_csv(args.df2_path)

    merged_df1 = merged_collections.merge(
        df1, left_on=args.left_on, right_on=args.column1, how="left"
    )
    left_on_2 = f"{args.left_on}_2"
    df = merged_df1.merge(df2, left_on=left_on_2, right_on=args.column2, how="left")

    df = df[df[args.similarity_column_name] > args.similarity_threshold]
    df = df.drop(
        columns=[
            "embedding",
            "embedding_2",
            args.left_on,
            left_on_2,
            args.similarity_column_name,
        ]
    )
    df = df.drop_duplicates(subset="Non Nutrient Data.FDC Name")
    df.to_csv(args.output_path, index=False)


if __name__ == "__main__":
    main(args)
