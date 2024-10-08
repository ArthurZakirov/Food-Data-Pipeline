from langchain_community.document_loaders.pdf import PyPDFLoader as PDFLoader
from langchain.text_splitter import CharacterTextSplitter
import chromadb
import pandas as pd


from langchain_chroma import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import DataFrameLoader
from src.my_pandas.apply_lambda import aggregate_dataframe_columns


def load_documents_from_pdf_path(file_path, chunk_size=1000):
    pdf_loader = PDFLoader(file_path)
    documents = pdf_loader.load()
    splitter = CharacterTextSplitter(chunk_size=chunk_size)
    documents = splitter.split_documents(documents)
    return documents


def load_documents_from_dataframe_with_aggregation(
    dataframe,
    columns_to_aggregate,
):

    # If only one column is specified, use it directly as the source column
    if len(columns_to_aggregate) == 1:
        page_content_column = columns_to_aggregate[0]
    else:
        dataframe["aggregated_column"] = dataframe.apply(
            lambda row: aggregate_dataframe_columns(row, columns_to_aggregate), axis=1
        )
        page_content_column = "aggregated_column"

    loader = DataFrameLoader(
        data_frame=dataframe, page_content_column=page_content_column
    )

    # Load documents using the loader
    documents = loader.load()
    return documents


def create_or_load_embedding_database(embedding_config, documents):
    embedder = OpenAIEmbeddings(model=embedding_config.model)

    chroma = chromadb.PersistentClient(path=embedding_config.chroma.path)
    existing_collections = {col.name for col in chroma.list_collections()}

    print("\n\n\n\n")
    print(f"existing_collections: {existing_collections}")


    collection_name = embedding_config.chroma.collection_name
    if collection_name not in existing_collections:
        print(
            "\nCollection does not exist. Creating a new collection and adding documents."
        )
        embeddings = embedder.embed_documents(
            texts=[doc.page_content for doc in documents]
        )
        collection = chroma.get_or_create_collection(collection_name)

        print("Collection count before:", collection.count())
        collection.add(
            documents=[doc.page_content for doc in documents],
            embeddings=embeddings,
            ids=[str(i) for i in range(len(documents))],
            metadatas=[
                doc.metadata.update({"model": embedding_config.model})
                for doc in documents
            ],
        )
        print("Collection count after:", collection.count())
    else:
        collection = chroma.get_or_create_collection(collection_name)
        print(
            "\nCollection already exists. No new documents were added and embeddings were not computed."
        )
        print("Collection count:", collection.count())
        print("Collection name:", collection_name)

    db = Chroma(
        client=chroma,
        embedding_function=embedder,
        collection_name=embedding_config.chroma.collection_name,
    )
    return db


def load_pdf_retriever(embedding_config):
    documents = load_documents_from_pdf_path(embedding_config.data.path)
    db = create_or_load_embedding_database(embedding_config, documents)
    retriever = db.as_retriever()
    return retriever


def load_csv_retriever(embedding_config):
    dataframe = pd.read_csv(embedding_config.data.path).loc[
        : embedding_config.data.n_rows
    ]

    documents = load_documents_from_dataframe_with_aggregation(
        dataframe, embedding_config.data.columns_to_aggregate
    )
    db = create_or_load_embedding_database(embedding_config, documents)
    retriever = db.as_retriever()
    return retriever
