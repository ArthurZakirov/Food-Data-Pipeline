import json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import (
    PipelinePromptTemplate,
    FewShotChatMessagePromptTemplate,
    FewShotPromptTemplate,
    PromptTemplate,
)
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
)
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers.string import StrOutputParser
from langchain_openai.output_parsers import (
    JsonOutputKeyToolsParser,
    JsonOutputToolsParser,
)

from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Union


from src.my_langchain.embedding import load_pdf_retriever, load_csv_retriever
from src.my_langchain.output_parsers_utils import create_custom_response_schema_list


class InputChat(BaseModel):
    """Input for the chat endpoint."""

    messages: List[Union[HumanMessage, AIMessage, SystemMessage]] = Field(
        ...,
        description="The chat messages representing the current conversation.",
    )


def build_model_from_config(model_config) -> Runnable:
    if model_config.provider == "openai":
        model = ChatOpenAI(
            model=model_config.name, temperature=model_config.temperature
        )
    else:
        model = ChatOpenAI(
            model=model_config.name, temperature=model_config.temperature
        )
    return model


def build_prompt_from_config(prompt_config) -> Runnable:

    from src.config.utils import to_native_python

    example_prompt = PromptTemplate.from_template(
        prompt_config.pipeline_prompts.examples_prompt.example_prompt
    )

    examples_prompt = FewShotPromptTemplate(
        examples=to_native_python(
            prompt_config.pipeline_prompts.examples_prompt.examples
        ),
        example_prompt=example_prompt,
        input_variables=example_prompt.input_variables,
        suffix=prompt_config.pipeline_prompts.examples_prompt.suffix,
    )

    pipeline_prompts = [
        (
            "system",
            PromptTemplate.from_template(prompt_config.pipeline_prompts.system_message),
        ),
        (
            "instructions",
            PromptTemplate.from_template(prompt_config.pipeline_prompts.instructions),
        ),
        ("examples", examples_prompt),
        # ("Input", PromptTemplate.from_template("{Input}")),
    ]

    final_prompt = PromptTemplate.from_template(prompt_config.final_prompt)

    pipeline_prompt = PipelinePromptTemplate(
        pipeline_prompts=pipeline_prompts, final_prompt=final_prompt
    )

    return pipeline_prompt


def build_output_parser_from_config(chain_config):
    if chain_config.output_parser == "JsonOutputKeyToolsParser":
        output_parser = JsonOutputKeyToolsParser(
            key_name=chain_config.response_schema.name
        )

    elif chain_config.output_parser == "JsonOutputToolsParser":
        output_parser = JsonOutputToolsParser()

    else:
        output_parser = StrOutputParser()
    return output_parser


def build_retrieve_and_passthrough_from_config(config) -> Runnable:
    if config.embedding.data.path.endswith(".pdf"):
        load_retriever = load_pdf_retriever

    elif config.embedding.data.path.endswith(".csv"):
        load_retriever = load_csv_retriever

    retrieve_and_passthrough = RunnableParallel(
        {
            "question": RunnablePassthrough(),
            "context": load_retriever(config.embedding)
            | RunnableLambda(
                lambda docs: "\n\n".join([doc.page_content for doc in docs])
            ),
        }
    )
    return retrieve_and_passthrough


def build_input_type_from_config_inplace(chain, chain_config):
    if chain_config.input_type == "chat_history_to_str":
        return chain.with_types(input_type=InputChat)

    elif chain_config.input_type == "last_chat_message_str_from_chat":
        return chain.with_types(input_type=InputChat) | RunnableLambda(
            lambda chat_messages: chat_messages[-1].to_string()
        )

    elif chain_config.input_type == "string":
        return chain.with_types(input_type=str)

    elif chain_config.input_type == "dict":
        return chain.with_types(input_type=dict)


def build_rag_chain_from_config(config) -> Runnable:

    prompt = build_prompt_from_config(config.chain.prompt)
    retrieve_and_passthrough = build_retrieve_and_passthrough_from_config(config)

    model = build_model_from_config(config.chain.model)

    output_parser = build_output_parser_from_config(config.chain)

    chain = retrieve_and_passthrough | prompt | model | output_parser
    chain = build_input_type_from_config_inplace(chain, config.chain)
    return chain
