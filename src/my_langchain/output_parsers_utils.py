from langchain.pydantic_v1 import BaseModel, Field, create_model
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_openai.output_parsers import (
    JsonOutputKeyToolsParser,
    JsonOutputToolsParser,
)
import pandas as pd
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


def create_custom_response_schema(name, fields):
    fields = {
        field.name: (field.type, Field(default=None, description=field.description))
        for field in fields
    }
    return create_model(name, **fields)


def create_custom_response_schema_list(name, fields):
    CustomSchema = create_custom_response_schema(name, fields)
    fields = {
        "items": (
            list[CustomSchema],
            Field(default=None, description="List of custom schemas"),
        )
    }
    return create_model(f"{name}List", **fields)


def create_output_parser_from_response_schema_dict(
    response_schemas, name_str="field", description_str="description"
):
    output_parser = StructuredOutputParser.from_response_schemas(
        [
            ResponseSchema(name=schema[name_str], description=schema[description_str])
            for schema in response_schemas
        ]
    )
    return output_parser
