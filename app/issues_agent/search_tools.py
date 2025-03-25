from typing import List
from issues_agent.issues_tools import _get_account_id_from_email, _create_jira_urlified_list
import json
import logging
from jira_client.client import JiraClient

from issues_agent.issues_models import JiraIssueOutput


def _retrieve_multiple_jira_issues(user_email: str, project: str, num_jira_issues_to_retrieve: int) -> List:
  """
  Retrieve the latest Jiras for a given user and project.

  Args:
    user_email (str): The email of the user.
    project (str): The Jira project to search in.
    num_jira_issues_to_retrieve (int, optional): The number of tickets to retrieve.

  Returns:
    List: A list of the top n jiras.
  """
  logging.info(f"Retrieving top {num_jira_issues_to_retrieve} Jiras in Project {project} for user: {user_email}")

  if "@" not in user_email or "." not in user_email:
    logging.info("invalid email address.")
    return []

  try:
    jira_api = JiraClient.get_jira_instance()
    account_id = _get_account_id_from_email(user_email)
    logging.info(f"Account ID for user {user_email}: {account_id}")
    issues = jira_api.search_issues(
      f"project={project} AND (reporter='{account_id}' OR assignee='{account_id}') ORDER BY created DESC",
      maxResults=num_jira_issues_to_retrieve,
    )
    issues_md_list = _create_jira_urlified_list(issues)
    logging.info(f"Issues found: {issues_md_list}")
    return issues_md_list
  except Exception as e:
    logging.error(f"Error retrieving service desk tickets: {e}")
    return []

def retrieve_multiple_jira_issues(user_email: str, project: str, num_jira_issues_to_retrieve: int) -> JiraIssueOutput:
  """
  Retrieve the latest n Jiras for a given user and project.

  Args:
    user_email (str): The email of the user.
    project (str): The Jira project to search in.
    num_jira_issues_to_retrieve (int, optional): The number of tickets to retrieve. Default 5

  Returns:
    List: A list of the top n service desk tickets.
  """
  resp_str = _retrieve_multiple_jira_issues(user_email, project, num_jira_issues_to_retrieve)
  return JiraIssueOutput(response=json.dumps(resp_str, indent=2))

def _search_jira_issues_using_jql(jql_query: str, user_email: str) -> List:
  """
  Search for Jira tickets based on a JQL query and user_email.

  Args:
    jql_query (str): The JQL query string.
    user_email (str): The email of the user.

  Returns:
    list: List of Jira issue IDs in a markdown format.
  """
  logging.info(f"Searching tickets with JQL: {jql_query} for user: {user_email}")
  try:
    jira_api = JiraClient.get_jira_instance()
    issues = jira_api.search_issues(jql_query)
    logging.info(f"Issues found: {issues}")
    if not issues:
      return "Seems like there are no tickets to display with your query."
    issues_md_list = _create_jira_urlified_list(issues)
    return issues_md_list
  except Exception as e:
    logging.error(f"Error in ticket retrieval tool: {e}")
    return "An error occurred while retrieving tickets."

def search_jira_issues_using_jql(jql_query: str, user_email: str) -> JiraIssueOutput:
  """
  Search for Jira tickets based on a JQL query and user_email.

  Args:
    jql_query (str): The JQL query string.
    user_email (str): The email of the user.

  Returns:
    list: List of Jira issue IDs in a markdown format.
  """
  return JiraIssueOutput(response=_search_jira_issues_using_jql(jql_query, user_email))