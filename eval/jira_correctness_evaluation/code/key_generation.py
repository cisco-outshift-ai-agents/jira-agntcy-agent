import json
from langchain_openai import AzureChatOpenAI
from typing_extensions import Annotated, TypedDict, Optional
from langchain.prompts import PromptTemplate
import yaml
import os
import sys
import logging
import fire


def llm_initialize(AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT):

    """
    This initialized the Azure LLM.

    Args:
        AZURE_OPENAI_API_KEY (str): AZURE_OPENAI_API_KEY string.
        AZURE_OPENAI_ENDPOINT (str): AZURE_OPENAI_ENDPOINT string

    Returns:
        azure_llm instance
    """

    azure_llm = AzureChatOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2023-05-15",
    )

    return azure_llm


class Output(TypedDict):
    """
    Structured output of LLM. This returns project_name, project_key, issue_name when used in addition to prompt template.
    """

    project_name: Annotated[Optional[str], "", "The project name"]
    project_key: Annotated[Optional[str], "", "The project key"]
    issue_name: Annotated[Optional[str], "", "The issue name"]


def prompt_template_get_key(query):

    """
    This takes the user query and returns either the project_name, project_key or issue_name.

    Args:
        query (str): The user query.

    Returns:
        returns either the project_name, project_key or issue_name.
    """

    judge_prompt_template = """HUMAN:
    Given a {query}, please return the project name, project key or issue name if it is present in the query else return "".
    The project name or project key or issue name will be present in the query itself, do not make up any answer outside the query.

    Format the output as a valid JSON with the following keys:
    project_name
    project_key
    issue_name 

    Do nor change anything in the output. Please return as it is.

    ANSWER:"""

    judge_prompt = PromptTemplate.from_template(judge_prompt_template)

    return judge_prompt


def main(config_file="key_generation_config.yml", **kwargs):

    config = yaml.safe_load(open(config_file, "r"))

    GPT_DEPLOYMENT_NAME = config["GPT_DEPLOYMENT_NAME"]
    AZURE_OPENAI_API_KEY = config["AZURE_OPENAI_API_KEY"]
    AZURE_OPENAI_ENDPOINT = config["AZURE_OPENAI_ENDPOINT"]

    if not GPT_DEPLOYMENT_NAME or not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
        print(
            "Error: All GPT_DEPLOYMENT_NAME, AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables must be set."
        )
        sys.exit(1)

    azure_llm = llm_initialize(AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT)
    structured_llm = azure_llm.with_structured_output(Output)

    initial_queries_file_path = config["INITIAL_QUERIES_FILE"]

    # Read the file as a JSON string
    with open(initial_queries_file_path, 'r') as file:
        json_string = file.read()

    initial_data = json.loads(json_string)

    final_dict_list = []

    for dictionary in initial_data:
        query = dictionary["query"]
        judge_prompt = prompt_template_get_key(query)
        op_content = structured_llm.invoke(judge_prompt.format(query=query))
        combined_dict = dictionary | op_content
        final_dict_list.append(combined_dict)

    file_key_output_path = config["FINAL_OUTPUT_QUERIES_FILE"]

    with open(file_key_output_path, "w") as file:
        json.dump(final_dict_list, file, indent=4)


if __name__ == "__main__":
    fire.Fire(main)