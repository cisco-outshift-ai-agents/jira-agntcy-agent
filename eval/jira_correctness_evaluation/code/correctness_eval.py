from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from typing_extensions import Annotated, TypedDict, Optional
import os
import sys
import json
import yaml
import fire


def llm_initialize(AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT):

    """
    This initialized the Azure LLM.

    Args:
        AZURE_OPENAI_API_KEY (str): AZURE_OPENAI_API_KEY string.
        AZURE_OPENAI_ENDPOINT (str): AZURE_OPENAI_ENDPOINT string

    Returns:
        return azure_llm
    """

    azure_llm = AzureChatOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2023-05-15",
    )

    return azure_llm


def prompt_template_agent_ground_truth(query, ground_truth, jira_agent_response): 

    """
    This is the prompt template which takes the query, ground_truth, jira_agent_response for evaluation.

    Returns:
        returns the prompt_template.

    """

    judge_prompt_template = """HUMAN:
    <role> You are an expert reviewer performing comparison of an agent response: {jira_agent_response} and ground truth: {ground_truth} which are both responses to the query: {query}. 
    Please give a rating out of 5 how close is the agent_response to the ground_truth and reason for the rating.

    Format the output as a valid JSON with the following keys:
    rating
    reasoning

    ANSWER:"""

    judge_prompt = PromptTemplate.from_template(judge_prompt_template)

    return judge_prompt


def prompt_template_query_metadata(query, metadata_before, metadata_after, jira_agent_response): 

    """
    This is the prompt template which takes the query, metadata_before, metadata_after for evaluation.

    Returns:
        returns the prompt_template.

    """

    judge_prompt_template = """HUMAN:
    <role> You are an expert reviewer performing comparison of previous metadata: {metadata_before} and post metadata: {metadata_after} where previous metadata
    is before the query: {query} has been executed and post metadata is after the query has been executed by an agent whose response is: {jira_agent_response}. 
    Please give a rating out of 5 on how well based on the previous metadata, query and agent response, the post metadata reflects the answer of the query and also give a reason for the rating.

    Format the output as a valid JSON with the following keys:
    rating
    reasoning

    ANSWER:"""

    judge_prompt = PromptTemplate.from_template(judge_prompt_template)

    return judge_prompt


class Rating(TypedDict):
    """Rating to tell to the user"""

    rating: Annotated[Optional[int], None, "The rating, from 1 to 5"]
    reasoning: Annotated[str, ..., "The reasoning behind the rating"]


def write_table_to_md(data, file_path):
    if not data:
        print("No data to write to the Markdown file.")
        return

    # Extract the headers from the keys of the first dictionary
    headers = data[0].keys()

    # Build the Markdown table header
    table_header = "| " + " | ".join(headers) + " |"
    table_separator = "| " + " | ".join(["---"] * len(headers)) + " |"

    # Build the table rows
    table_rows = []
    for row in data:
        table_rows.append("| " + " | ".join(str(row[col]) for col in headers) + " |")

    # Combine the header, separator, and rows
    markdown_table = "\n".join([table_header, table_separator] + table_rows)

    # Write to the Markdown file
    with open(file_path, "w") as md_file:
        md_file.write(markdown_table)

    print(f"Table written to {file_path}")


def main(config_file="correctness_eval_config.yml", **kwargs):

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
    structured_llm = azure_llm.with_structured_output(Rating)

    jira_action_replay_output = config['JIRA_ACTION_REPLAY_OUTPUT']
    with open(jira_action_replay_output, "r") as file:
        loaded_data = json.load(file)

    final_dictionary = []
    rating_list = []

    for dictionary in loaded_data:

        query = dictionary["query"]

        if "ground_truth" in dictionary:
            ground_truth = dictionary["ground_truth"]
            jira_agent_response = dictionary["jira_agent_response"]
            judge_prompt = prompt_template_agent_ground_truth(query, ground_truth, jira_agent_response)
            op_content = structured_llm.invoke(
                    judge_prompt.format(query=query, ground_truth=ground_truth, jira_agent_response=jira_agent_response)
                )
            keys = list(op_content.keys())
            key_0 = keys[0].strip()
            key_1 = keys[1].strip()
            op = {
                    "query": query,
                    "rating": op_content[key_0],
                    "reasoning": op_content[key_1],
                    "ground_truth": ground_truth,
                    "jira_agent_response": jira_agent_response
                }
            rating_list.append(op_content[key_0])
            final_dictionary.append(op)

        elif "metadata_before" in dictionary:
            metadata_before = dictionary["metadata_before"]
            metadata_after = dictionary["metadata_after"]
            jira_agent_response = dictionary["jira_agent_response"]
            judge_metadata_prompt = prompt_template_query_metadata(query, metadata_before, metadata_after, jira_agent_response)
            op_meta_content = structured_llm.invoke(
                    judge_metadata_prompt.format(query=query, metadata_before=metadata_before, metadata_after=metadata_after, jira_agent_response=jira_agent_response)
                )
            keys_meta = list(op_meta_content.keys())
            key_meta_0 = keys_meta[0].strip()
            key__meta_1 = keys_meta[1].strip()
            op_meta = {
                    "query": query,
                    "rating": op_meta_content[key_meta_0],
                    "reasoning": op_meta_content[key__meta_1],
                    "metadata_before": metadata_before,
                    "metadata_after": metadata_after,
                    "jira_agent_response": jira_agent_response
                }
            rating_list.append(op_meta_content[key_meta_0])
            final_dictionary.append(op_meta)

    average_rating_list = sum(rating_list) / len(rating_list)
    max_value = 5
    percentage = (average_rating_list / max_value) * 100

    rating_file_name = f"{config["RATING_FILE_NAME"]}_{config["GPT_DEPLOYMENT_NAME"]}.json"

    with open(rating_file_name, "w") as file:
        json.dump(final_dictionary, file, indent=4)

    table_data = [{"Total_Queries:": len(rating_list), "max_value:": max_value, "Average Rating:": average_rating_list, "Percentage:": percentage}]

    report_file = f"{config["REPORT_FILE_NAME"]}_{config["GPT_DEPLOYMENT_NAME"]}.md"

    write_table_to_md(table_data, report_file)


if __name__ == "__main__":
    fire.Fire(main)