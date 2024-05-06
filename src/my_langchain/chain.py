import json
from src.my_langchain.chain_components import (
    build_prompt_from_config,
    build_model_from_config,
    build_output_parser_from_config,
    create_custom_response_schema_list,
    build_retrieve_and_passthrough_from_config,
    build_input_type_from_config_inplace,
)


def build_rag_chain_from_config(config):

    prompt = build_prompt_from_config(config.chain.prompt)
    retrieve_and_passthrough = build_retrieve_and_passthrough_from_config(config)

    model = build_model_from_config(config.chain.model)

    output_parser = build_output_parser_from_config(config.chain)

    chain = retrieve_and_passthrough | prompt | model | output_parser
    chain = build_input_type_from_config_inplace(chain, config.chain)
    return chain


def build_data_processing_chain_from_config(chain_config, verbose=False):
    prompt = build_prompt_from_config(chain_config.prompt)

    response_schema = create_custom_response_schema_list(
        chain_config.response_schema.name,
        chain_config.response_schema.fields,
    )

    model = build_model_from_config(chain_config.model)
    output_parser = build_output_parser_from_config(chain_config)

    chain = prompt | model.bind_tools([response_schema]) | output_parser

    return chain


def build_chain_from_config(chain_config):
    if chain_config.type == "rag":
        return build_rag_chain_from_config(chain_config)
    elif chain_config.type == "data_processing":
        return build_data_processing_chain_from_config(chain_config)
