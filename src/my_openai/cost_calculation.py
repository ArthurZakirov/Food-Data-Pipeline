def calculate_cost_of_processing_df_column(df, column_name, model):
    dollar_per_token = {
        "gpt-4-turbo": {"input": 10.00 / 10e5, "output": 30.00 / 10e5},
        "gpt-3.5-turbo": {"input": 0.50 / 10e5, "output": 1.50 / 10e5},
        "text-embedding-3-small": {"input": 0.02 / 10e5},
        "text-embedding-3-large": {"input": 0.13 / 10e5},
        "ada v2": {"input": 0.10 / 10e5},
    }

    tokens_per_word = 1000 / 750
    num_input_words = df[column_name].apply(lambda x: len(x.split(" "))).sum()
    input_cost = dollar_per_token[model]["input"] * tokens_per_word * num_input_words
    return input_cost
