def aggregate_dataframe_columns(
    row, columns_to_aggregate, delimiter="\n", with_column_names=True
):
    if with_column_names:
        return delimiter.join([f"{col}: {row[col]}" for col in columns_to_aggregate])
    else:
        return delimiter.join([row[col] for col in columns_to_aggregate])
