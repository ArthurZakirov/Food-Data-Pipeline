import pandas as pd
import chromadb
from scipy.spatial.distance import cosine
from tqdm import tqdm

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist


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
    return df


def merge_embeddings_on_similarity(df1, df2):
    # Resetting indices to ensure they are sequential
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)

    embeddings1 = np.stack(df1["embedding"].values)
    embeddings2 = np.stack(df2["embedding"].values)

    # Compute the similarity matrix
    similarity_matrix = 1 - cdist(embeddings1, embeddings2, metric="cosine")

    closest_matches = []
    for i, row1 in df1.iterrows():
        if i < similarity_matrix.shape[0]:  # Ensuring the index is within bounds
            best_match_idx = np.argmax(similarity_matrix[i])
            best_similarity = similarity_matrix[i][
                best_match_idx
            ]  # Ensure correct indexing
            row2 = df2.iloc[best_match_idx].to_dict()
            merged_row = {
                **row1.to_dict(),
                **{f"collection2_{k}": v for k, v in row2.items()},
                "similarity": best_similarity,
            }
            closest_matches.append(merged_row)
        else:
            pass
    merged_df = pd.DataFrame(closest_matches)
    return merged_df


# MERGE REWE AND FDC DATA USING EMBEDDINGS
# similarity_threshold = 0.8
# path = "data/processed/chroma.db"
# collection1_name = "rewe_data"
# collection2_name = "fdc_data"
# df1_path = "data/processed/cleaned_rewe_dataset_with_extracted_names.csv"
# df2_path = "data/processed/fdc_data.csv"
# column1 = "Non Nutrient Data.Regulated Name English"
# column2 = "Non Nutrient Data.FDC Name"
# left_on = "document_id"
# left_on_2 = "collection2_document_id"
# output_path = "data/processed/merged_rewe_fdc_data.csv"

# MERGE REWE+FDC AND INSULIN INDEX DATA USING EMBEDDINGS
similarity_threshold = 0.5
path = "data/processed/chroma.db"
collection1_name = "rewe_fdc"
collection2_name = "insulin_index_data"
df1_path = "data/processed/merged_rewe_fdc_data.csv"
df2_path = "data/processed/insulin_index.csv"
column1 = "Non Nutrient Data.FDC Name"
column2 = "Insulin Index Food Name"
left_on = "document_id"
left_on_2 = "collection2_document_id"
output_path = "data/processed/merged_rewe_fdc_insulin.csv"


collection_df1 = load_chroma_collection(path, collection1_name)
collection_df1 = collection_df1.drop_duplicates(subset=["document_id"], keep="first")

collection_df2 = load_chroma_collection(path, collection2_name)

merged_collections = merge_embeddings_on_similarity(collection_df1, collection_df2)
# print(merged_collections)
df1 = pd.read_csv(df1_path)
df1 = df1.drop_duplicates(subset=["Non Nutrient Data.FDC Name"], keep="first")
# df1.columns = ["Non Nutrient Data." + col for col in df1.columns]


df2 = pd.read_csv(df2_path)

merged_df1 = merged_collections.merge(
    df1, left_on=left_on, right_on=column1, how="left"
)

final_merged_df = merged_df1.merge(df2, left_on=left_on_2, right_on=column2, how="left")

df = final_merged_df


df = df[df["similarity"] > similarity_threshold]
df = df.drop(columns=["embedding", "collection2_embedding", "document_id"])
df = df.rename(columns={"collection2_document_id": "FDC Name"})
df = df.drop(columns=["FDC Name", "similarity"])
df = df.drop_duplicates(subset="Non Nutrient Data.FDC Name")

df.to_csv(output_path, index=False)
