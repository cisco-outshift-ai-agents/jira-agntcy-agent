import json
import yaml
from jira import JIRA
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
import os
import sys
from typing_extensions import Annotated, TypedDict, Optional
from langchain.prompts import PromptTemplate
import time
import fire
import subprocess


def get_jira_instance(jira_url, username, api_token):
    jira = JIRA(server=jira_url, basic_auth=(username, api_token))
    return jira


def get_metadata_issue(issue_key, jira):
    if issue_key:
        issue = jira.issue(issue_key)
        raw_issue_data = issue.raw
        raw_issue_as_string = str(raw_issue_data)
        return raw_issue_as_string
    else:
        return ""


def get_metadata_project_key(project_key, jira):
    project = jira.project(project_key)
    if project:
        raw_project_data = project.raw
        raw_project_as_string = str(raw_project_data)
        return raw_project_as_string
    else:
        return ""


def get_metadata_project_name(project_name, jira):
    projects = jira.projects()
    project = next((p for p in projects if p.name == project_name), None)
    if project:
        key = project.key
        raw_project_as_string = get_metadata_project_key(key, jira)
        return raw_project_as_string
    else:
        return ""


def get_issue_transitions(issue_key, jira):
    transitions = jira.transitions(issue_key)
    transitions_dic_list = []
    for transition in transitions:
        transitions_dic = {"ID": transition['id'], "Name": transition['name']}
        transitions_dic_list.append(transitions_dic)
    return transitions_dic_list


def get_jql_query_issue(jql_query, jira):
    issues = jira.search_issues(jql_query)
    # Process the results
    issues_dic_list = []
    for issue in issues:
        issues_dic = {"Issue Key": issue.key, "Summary": issue.fields.summary}
        issues_dic_list.append(issues_dic)
    return issues_dic_list


def llm_initialize(AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT):

    """
    This initialized the Azure LLM.

    Args:
        AZURE_OPENAI_API_KEY (str): AZURE_OPENAI_API_KEY string.
        AZURE_OPENAI_ENDPOINT (str): AZURE_OPENAI_ENDPOINT string

    Returns:
        return azure_llm instance.
    """

    azure_llm = AzureChatOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2023-05-15",
    )

    return azure_llm


def get_jira_agent_response(query, jira):

    # Define your curl command as a list of arguments
    print(query)
    json_data = {
                "agent_id": "remote_agent",
                "input": {
                    "query": query
                },
                "metadata": {"id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}
            }
    json_string = json.dumps(json_data)

    curl_command = [
        "curl",
        "-X", "POST",  # HTTP method
        'http://0.0.0.0:8125/api/v1/runs',  # URL
        "-H", "accept: application/json",  # Header
        "-H", "Content-Type: application/json",  # Header
        "-d", json_string
    ]

    # Execute the curl command
    try:
        result = subprocess.run(curl_command, text=True, capture_output=True, check=True)
        subprocess_output = result.stdout
        print("Response:")
        print(subprocess_output)  # Print the response from the server
        subprocess_json_object = json.loads(subprocess_output)
        if "output" in subprocess_json_object:
            print(subprocess_json_object["output"])
            return subprocess_json_object["output"]
        else:
            return subprocess_json_object
    except subprocess.CalledProcessError as e:
        print("Error occurred:")
        print(e.stderr)  # Print the error message
        return e.stderr


class Output(TypedDict):
    """Structured output that returns the issue name."""
    issue_name: Annotated[Optional[str], "", "The issue name"]


def prompt_template_get_key(query): 

    judge_prompt_template = """HUMAN:
    Given a {query}, please return the issue name if it is present in the query else return "".
    The issue name will be present in the query itself as a part of a URL, do not make up any answer outside the query.

    Format the output as a valid JSON with the following keys:
    issue_name

    Do not change anything in the output. Please return as it is.

    ANSWER:"""

    judge_prompt = PromptTemplate.from_template(judge_prompt_template)
    return judge_prompt


class OutputJQL(TypedDict):
    """Structured output that returns the JQL query."""
    jql_query: Annotated[Optional[str], "", "The Jira Query Language (JQL) query"]


def prompt_template_get_jql(query):

    judge_prompt_template = """HUMAN:
    Given a {query}, please return the Jira Query Language (JQL) if it is present in the query else return "".
    The JQL will be present in the query itself, do not make up any answer outside the query.

    Format the output as a valid JSON with the following keys:
    jql_query 

    Do not change anything in the output. Please return as it is.

    ANSWER:"""

    judge_prompt = PromptTemplate.from_template(judge_prompt_template)
    return judge_prompt


def process_jira_action(initial_data, structured_llm, structured_llm_jira, jira):

    final_dict_list = []

    for dictionary in initial_data:

        query = dictionary["query"]
        action = dictionary["action"]
        project_name = dictionary["project_name"]
        project_key = dictionary["project_key"]
        issue_name = dictionary["issue_name"]
        time.sleep(15)

        if action == 'project_query':
            if project_name:
                ground_truth = get_metadata_project_name(project_name, jira)
                jira_agent_response = get_jira_agent_response(query, jira)
                op_content = {"ground_truth": ground_truth, "jira_agent_response": jira_agent_response}
                combined_dict = dictionary | op_content
                final_dict_list.append(combined_dict)
            elif project_key:
                ground_truth = get_metadata_project_key(project_key, jira)
                jira_agent_response = get_jira_agent_response(query, jira)
                op_content = {"ground_truth": ground_truth, "jira_agent_response": jira_agent_response}
                combined_dict = dictionary | op_content
                final_dict_list.append(combined_dict)

        if action == 'project_transition':
            if issue_name:
                ground_truth = get_issue_transitions(issue_name, jira)
                jira_agent_response = get_jira_agent_response(query, jira)
                op_content = {"ground_truth": ground_truth, "jira_agent_response": jira_agent_response}
                combined_dict = dictionary | op_content
                final_dict_list.append(combined_dict)

        if action == 'project_creation' or action == 'project_update' or action == 'project_assign':
            if project_name:
                metadata_before = get_metadata_project_name(project_name, jira)
                jira_agent_response = get_jira_agent_response(query, jira)
                metadata_after = get_metadata_project_name(project_name, jira)
                op_content = {"metadata_before": metadata_before, "metadata_after": metadata_after, "jira_agent_response": jira_agent_response}
                combined_dict = dictionary | op_content
                final_dict_list.append(combined_dict)
            elif project_key:
                metadata_before = get_metadata_project_key(project_key, jira)
                jira_agent_response = get_jira_agent_response(query, jira)
                metadata_after = get_metadata_project_key(project_key, jira)
                op_content = {"metadata_before": metadata_before, "metadata_after": metadata_after, "jira_agent_response": jira_agent_response}
                combined_dict = dictionary | op_content
                final_dict_list.append(combined_dict)

        if action == 'issue_update' or action == 'issue_assign':
            if issue_name:
                metadata_before = get_metadata_issue(issue_name, jira)
                jira_agent_response = get_jira_agent_response(query, jira)
                metadata_after = get_metadata_issue(issue_name, jira)
                op_content = {"metadata_before": metadata_before, "metadata_after": metadata_after, "jira_agent_response": jira_agent_response}
                combined_dict = dictionary | op_content
                final_dict_list.append(combined_dict)

        if action == 'issue_creation':
            metadata_before = ""
            jira_agent_response = get_jira_agent_response(query, jira)
            judge_prompt = prompt_template_get_key(jira_agent_response)
            op_dic = structured_llm.invoke(
                    judge_prompt.format(query=jira_agent_response)
                )
            final_issue_key = op_dic['issue_name']
            metadata_after = get_metadata_issue(final_issue_key, jira)
            op_content = {"metadata_before": metadata_before, "metadata_after": metadata_after, "jira_agent_response": jira_agent_response}
            combined_dict = dictionary | op_content
            final_dict_list.append(combined_dict)

        if action == 'issue_query':
            jira_agent_response = get_jira_agent_response(query, jira)
            jira_judge_prompt = prompt_template_get_jql(jira_agent_response)
            op_dic = structured_llm_jira.invoke(
                    jira_judge_prompt.format(query=jira_agent_response)
                )
            jql_query = op_dic["jql_query"]
            ground_truth = get_jql_query_issue(jql_query, jira)
            op_content = {"ground_truth": ground_truth, "jira_agent_response": jira_agent_response}
            combined_dict = dictionary | op_content
            final_dict_list.append(combined_dict)

    return final_dict_list


def main(config_file="jira_action_replay.yml", **kwargs):

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

    jira_server = config["JIRA_SERVER"]
    jira_user = config["JIRA_USER"]
    jira_api_token = config["JIRA_API_TOKEN"]
    jira = get_jira_instance(jira_server, jira_user, jira_api_token)

    key_generation_file_path = config['KEY_GENERATION_FILE_PATH']

    with open(key_generation_file_path, 'r') as file:
        json_string = file.read()

    initial_data = json.loads(json_string)

    structured_llm = azure_llm.with_structured_output(Output)
    structured_llm_jira = azure_llm.with_structured_output(OutputJQL)

    final_dict_list = process_jira_action(initial_data, structured_llm, structured_llm_jira, jira)

    jira_action_replay_output = config["JIRA_ACTION_REPLAY_OUTPUT"]

    with open(jira_action_replay_output, "w") as file:
        json.dump(final_dict_list, file, indent=4)


if __name__ == "__main__":
    fire.Fire(main)
