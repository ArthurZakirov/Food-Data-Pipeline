import pandas as pd


def flatten_columns_inplace(df, delimiter="."):
    df.columns = [delimiter.join(map(str, col)).strip() for col in df.columns.values]
    return df


def unflatten_columns_inplace(df, delimiter="."):
    df.columns = pd.MultiIndex.from_tuples(
        [tuple(c.split(delimiter)) for c in df.columns]
    )
    return df
