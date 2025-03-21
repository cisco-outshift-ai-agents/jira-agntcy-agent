import logging
import os
from jira_client.client import JiraClient, JiraRESTClient
import requests
from requests.auth import HTTPBasicAuth
import json
from issues_agent.issues_models import CreateJiraIssueInput, JiraIssueOutput
from core.config import INTERNAL_ERROR_MESSAGE

def get_jira_issue_metadata(project_key: str) -> JiraIssueOutput:
  """
  Create a new generic Jira issue.

  Args:
      project_key (str): The project key for the Jira issue metadata.

  Returns:
      str: The URL of the created Jira issue.
  """
  logging.info(f"Getting metadata for project: {project_key}")

  try:
    jira_api = JiraClient.get_jira_instance()
    issue_metadata = jira_api.createmeta(projectKeys=project_key, expand='projects.issuetypes.fields')
    supported_issue_types = {}
    for project in issue_metadata['projects']:
      for issue in project['issuetypes']:
        required_fields = {k: v for k, v in issue['fields'].items() if v['required']}
        supported_issue_types[issue['name']] = required_fields
    output = "".join([f"{issue_type}: {fields}" for issue_type, fields in supported_issue_types.items()])
    return JiraIssueOutput(response=output)
  except Exception as e:
    logging.error(f"Error getting Jira issue metadata: {e}")
    return JiraIssueOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

def create_jira_issue(input: CreateJiraIssueInput) -> JiraIssueOutput:
  """
  Create a new generic Jira issue.

  Args:
      input (CreateJiraIssueInput): The input model containing the details for creating the issue.

  Returns:
      str: The URL of the created Jira issue.
  """
  logging.info(f"Creating a new Jira issue in project: {input.project_key}")

  try:
    supported_issue_types = _get_supported_issue_types(input.project_key)
    if input.issue_type not in supported_issue_types:
      return JiraIssueOutput(response=f"Unsupported issue type: {input.issue_type}. Supported issue types are: {supported_issue_types}")

    reporter_id = _get_account_id_from_email(input.reporter_email)
    issue_dict = {
      'project': {'key': input.project_key},
      'summary': input.summary,
      'description': input.description,
      'issuetype': {'name': input.issue_type},
      #'reporter': {'id': reporter_id} # TODO: reported cannot be set for some reason, need to check
    }

    if input.assignee_email:
      issue_dict['assignee'] = {'id': _get_account_id_from_email(input.assignee_email)}

    jira_api = JiraClient.get_jira_instance()
    new_issue = jira_api.create_issue(fields=issue_dict)
    urlify_jira_issue_id = _urlify_jira_issue_id(new_issue.key)
    logging.info(f"Created new Jira issue: {urlify_jira_issue_id}")
    return JiraIssueOutput(response=urlify_jira_issue_id)
  except Exception as e:
    logging.error(f"Error creating Jira issue: {e}")
    return JiraIssueOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

def assign_jira(issue_key: str, assignee_email: str) -> JiraIssueOutput:
  """
  Assigns a JIRA ticket to a specified user.

  Args:
      issue_key (str): The key of the JIRA issue to assign.
      assignee_email (str): The email of the user to assign the issue to.

  Returns:
      JiraIssueOutput: The result of the assignment.
  """
  logging.info(f"Assigning JIRA ticket {issue_key} to {assignee_email}")

  jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
  try:
    assignee_url = f'{jira_server_url}/rest/api/3/issue/{issue_key}/assignee'
    payload = json.dumps({
      'accountId': _get_account_id_from_email(assignee_email)
    })
    response = requests.put(assignee_url, headers=headers, data=payload, auth=auth)
    if response.status_code == 204:
      urlify_jira_issue_id = _urlify_jira_issue_id(issue_key)
      logging.info(f'JIRA ticket {issue_key} assigned to {assignee_email} successfully.')
      return JiraIssueOutput(response=f"JIRA ticket assigned successfully {urlify_jira_issue_id}.")
    else:
      logging.error(f'Failed to assign JIRA ticket {issue_key} to {assignee_email}. Status code: {response.status_code}, Response: {response.text}')
      return JiraIssueOutput(response="Failed to assign JIRA ticket.")
  except Exception as e:
    logging.error(f'Failed to assign JIRA ticket {issue_key} to {assignee_email}. Error: {e}')
    return JiraIssueOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

def update_issue_reporter(issue_key: str, reporter_email: str) -> JiraIssueOutput:
  """
  Update the reporter of a Jira issue.

  Args:
      issue_key (str): Jira Issue ID.
      reporter_email (str): The email of the new reporter.

  Returns:
      str: A message indicating the result of the update.
  """
  logging.info(f"Updating reporter of ticket: {issue_key}")

  try:
    jira_api = JiraClient.get_jira_instance()
    reporter_id = _get_account_id_from_email(reporter_email)
    issue = jira_api.issue(issue_key)
    issue.update(reporter={'id': reporter_id})
    logging.info("Reporter updated successfully.")
    urlify_jira_issue_id = _urlify_jira_issue_id(issue_key)
    return JiraIssueOutput(response=f"Reporter updated successfully on Jira {urlify_jira_issue_id}.")
  except Exception as e:
    logging.error(f"Error updating reporter: {e}")
    return JiraIssueOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

def add_new_label_to_issue(issue_key: str, label: str) -> JiraIssueOutput:
  """
  Add a new label to a Jira issue.

  Args:
      issue_key (str): Jira Issue ID.
      label (str): The label to add.

  Returns:
      str: A message indicating the result of the operation.
  """
  return _add_new_label_to_issue(issue_key, label)

def get_jira_issue_details(issue_key: str) -> JiraIssueOutput:
  """
  Retrieve the details of a Jira ticket based on its key.

  Args:
      issue_key (str): Jira Issue ID.

  Returns:
      dict: A dictionary containing the details of the ticket.
  """
  logging.info(f"Retrieving details for ticket: {issue_key}")

  try:
    jira_api = JiraClient.get_jira_instance()
    issue = jira_api.issue(issue_key)
    urlify_jira_issue_id = _urlify_jira_issue_id(issue.key)
    ticket_details = {
      "key": urlify_jira_issue_id,
      "summary": issue.fields.summary,
      "description": issue.fields.description,
      "status": issue.fields.status.name,
      "priority": issue.fields.priority.name,
      "reporter": issue.fields.reporter.displayName,
      "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
      "created": issue.fields.created,
      "updated": issue.fields.updated,
    }
    logging.info(f"Ticket details: {ticket_details}")
    return JiraIssueOutput(response=ticket_details)

  except Exception as e:
    logging.error(f"Error retrieving Jira issue details: {e}")
    return JiraIssueOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

def _add_new_label_to_issue(issue_key: str, label: str) -> JiraIssueOutput:
  """
  Add a new label to a Jira issue.

  Args:
      issue_key (str): Jira Issue ID.
      label (str): The label to add.

  Returns:
      JiraIssueOutput: The result of the operation.
  """
  logging.info(f"Adding label '{label}' to ticket: {issue_key}")
  try:
    jira_api = JiraClient.get_jira_instance()
    issue = jira_api.issue(issue_key)
    issue.fields.labels.append(label)
    issue.update(fields={"labels": issue.fields.labels})
    logging.info("Label added successfully.")
    urlify_jira_issue_id = _urlify_jira_issue_id(issue_key)
    return JiraIssueOutput(response=f"Label added successfully on Jira {urlify_jira_issue_id}.")
  except Exception as e:
    logging.error(f"Error adding label: {e}")
    return JiraIssueOutput(response="Failed to add label.")

def _urlify_jira_issue_id(issue_id: str) -> str:
  """
  Convert a Jira issue ID to a URL.

  Args:
      issue_id (str): The Jira issue ID.

  Returns:
      str: The URL of the Jira issue.
  """
  jira_server =  os.getenv("JIRA_URL") or os.getenv("JIRA_INSTANCE")
  return f"{jira_server}/browse/{issue_id}"

def _create_jira_urlified_list(issues) -> list:
  """
  Create a list of Jira issues in Markdown format with clickable links.

  Args:
      issues (list): A list of Jira issue objects. Each object is expected to have a 'key' attribute
                     representing the issue key (e.g., "PROJECT-123").

  Returns:
      list: A list of strings, where each string is a Markdown-formatted link to a Jira issue.
            The format is "[ISSUE_KEY](ISSUE_URL)".
  """
  issues_md = []
  for issue in issues:
    issue_link = _urlify_jira_issue_id(issue.key)
    issue_summary = issue.fields.summary
    issues_md.append(f"[{issue.key}: {issue_summary}]({issue_link})")
  return issues_md

def _get_account_id_from_email(email: str) -> str:
  """
  Retrieves the account ID associated with a given email address in JIRA.

  Args:
      email (str): The email address of the user whose account ID is to be retrieved.

  Returns:
      str: The account ID of the user, as a string. Returns None if the user is not found or if an error occurs.

  Raises:
      Exception: If the JIRA API request fails or encounters an error. The exception will contain details about the failure, including the HTTP status code and response text (if available).
  """
  try:
    jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
    search_url = f'{jira_server_url}/rest/api/3/user/search'

    query = {
      'query': email
    }

    user_search_response = requests.get(
      search_url,
      headers=headers,
      params=query,
      auth=auth
    )

    if user_search_response.status_code == 200:
      users_data = user_search_response.json()
      if users_data:
        account_id = users_data[0].get('accountId')
        logging.info(f'Account ID found for email {email}: {account_id}')
        return account_id
      else:
        logging.warning(f'No users found with email {email}.')
        return None
    else:
      logging.error(f'Failed to retrieve user details for email {email}. Status code: {user_search_response.status_code}, Response: {user_search_response.text}')
      return None
  except Exception as e:
    logging.error(f'Failed to get account ID for email {email}. Error: {e}')
    return None

def get_account_id_from_email(email: str) -> str:
  """
  Retrieves the account ID associated with a given email address in JIRA.

  Args:
      email (str): The email address of the user whose account ID is to be retrieved.

  Returns:
      str: The account ID of the user, as a string. Returns None if the user is not found or if an error occurs.

  Raises:
      Exception: If the JIRA API request fails or encounters an error. The exception will contain details about the failure, including the HTTP status code and response text (if available).
  """
  return _get_account_id_from_email(email)


def _get_supported_issue_types(project_key: str) -> list[str]:
  """
  Retrieve supported issue types for Jira issues in a specific project.

  Args:
      project_key (str): The key of the project to get issue metadata for.

  Returns:
      list[str]: A list of supported issue types.

  Raises:
      ValueError: If there is an error retrieving the metadata.
  """
  try:
    jira_api = JiraClient.get_jira_instance()
    issue_metadata = jira_api.createmeta(projectKeys=project_key, expand='projects.issuetypes.fields')
    supported_issue_types = []
    for project in issue_metadata['projects']:
      for issue in project['issuetypes']:
        supported_issue_types.append(issue['name'])

    return supported_issue_types
  except Exception as e:
    raise ValueError(f"Error getting Jira issue metadata: {e}") from e