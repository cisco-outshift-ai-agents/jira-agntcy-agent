from typing import List, Any

import requests
import json
import logging

from issues_agent.issues_models import JiraIssueOutput
from jira_client.client import JiraRESTClient
from utils.dryrun_utils import dryrun_response
from issues_agent.dryrun.mock_responses import (
  MOCK_PERFORM_JIRA_TRANSITION_RESPONSE,
  MOCK_GET_REQUIRED_FIELDS_FOR_TRANSITION_RESPONSE,
  MOCK_GET_JIRA_TRANSITIONS_RESPONSE,
)

@dryrun_response(MOCK_GET_REQUIRED_FIELDS_FOR_TRANSITION_RESPONSE)
def _get_required_fields_for_transition(issue_key: str, transition_name: str) -> list[Any] | None:
  """
  Retrieves the required fields for a given transition in a JIRA issue.

  Args:
    issue_key (str): The key of the JIRA issue.
    transition_name (str): The name of the transition to check.

  Returns:
    list: A list of required fields for the transition.
          Returns None if an error occurs or if the transition is not found.
  """
  jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()

  try:
    transition_url = f'{jira_server_url}/rest/api/3/issue/{issue_key}/transitions?expand=transitions.fields'
    transition_response = requests.get(transition_url, headers=headers, auth=auth)

    if transition_response.status_code == 200:
      transitions_data = transition_response.json()
      transitions = transitions_data.get('transitions', [])

      for transition in transitions:
        if transition['name'].lower().replace('-', '') == transition_name.lower().replace('-', ''):
          fields = transition.get('fields', {})
          required_fields = [field_name for field_name, field_data in fields.items() if field_data.get('required')]
          logging.info(f'Required fields for transition {transition_name} on JIRA ticket {issue_key}: {required_fields}')
          return required_fields

      logging.warning(f"Transition '{transition_name}' not found for JIRA ticket {issue_key}.")
      return None
    else:
      logging.error(f'Failed to retrieve transitions for JIRA ticket {issue_key}. Status code: {transition_response.status_code}, Response: {transition_response.text}')
      return None
  except Exception as e:
    logging.error(f'Failed to retrieve transitions for JIRA ticket {issue_key}. Error: {e}')
    return None

@dryrun_response(MOCK_GET_JIRA_TRANSITIONS_RESPONSE)
def _get_jira_transitions(issue_key: str) -> list:
  """
  Retrieves available transitions for a given JIRA issue.

  Args:
    issue_key (str): The key of the JIRA issue.

  Returns:
    list: A list of dictionaries, where each dictionary represents a transition
          and contains the 'id' and 'name' of the transition.
          Returns None if an error occurs or if no transitions are found.
  """
  jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()

  try:
    transition_url = f'{jira_server_url}/rest/api/3/issue/{issue_key}/transitions'
    transition_response = requests.get(transition_url, headers=headers, auth=auth)

    if transition_response.status_code == 200:
      transitions_data = transition_response.json()
      transitions = transitions_data.get('transitions', [])
      transition_list = [{'id': transition['id'], 'name': transition['name']} for transition in transitions]
      logging.info(f'Available transitions for JIRA ticket {issue_key}: {transition_list}')
      return transition_list
    else:
      logging.error(f'Failed to retrieve transitions for JIRA ticket {issue_key}. Status code: {transition_response.status_code}, Response: {transition_response.text}')
      return None
  except Exception as e:
    logging.error(f'Failed to retrieve transitions for JIRA ticket {issue_key}. Error: {e}')
    return None

def get_jira_transitions(issue_key: str) -> JiraIssueOutput:
  """
  Retrieves available transitions for a given JIRA issue.

  Args:
    issue_key (str): The key of the JIRA issue.

  Returns:
    list: A list of dictionaries, where each dictionary represents a transition
          and contains the 'id' and 'name' of the transition.
          Returns None if an error occurs or if no transitions are found.
  """
  transition_list = _get_jira_transitions(issue_key=issue_key)
  logging.info(f'Available transitions for JIRA ticket {issue_key}: {transition_list}')
  if transition_list:
    resp_str = f"Available transitions for JIRA ticket {issue_key}: {json.dumps(transition_list, indent=2)}"
    return JiraIssueOutput(response=resp_str)

  return JiraIssueOutput(response="Failed to retrieve transitions for JIRA ticket.")

@dryrun_response(MOCK_PERFORM_JIRA_TRANSITION_RESPONSE)
def _perform_jira_transition(
        issue_key: str,
        resolution_id: str,
        transition_name: str
) -> str:
  """
  Transitions a JIRA ticket to a specified state.

  Args:
      issue_key (str): The key of the JIRA issue to transition.
      transition_name (str): The name of the transition to perform.
      resolution_id (str, optional): The ID of the resolution to set when transitioning to a resolved state. Defaults to None.

  Returns:
      str: A message indicating the result of the transition.

  Raises:
      Exception: If the JIRA API request fails or encounters an error. The exception will contain details about the failure, including the HTTP status code and response text (if available).
  """
  logging.info(f'Attempting to transition JIRA ticket {issue_key} to state {transition_name} with resolution ID {resolution_id}.')
  jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()

  try:
    transition_url = f'{jira_server_url}/rest/api/3/issue/{issue_key}/transitions'
    available_transitions = _get_jira_transitions(issue_key)
    if not available_transitions:
      raise Exception(f"No transitions found for JIRA ticket {issue_key}.")

    transition_id = None
    for transition in available_transitions:
      if transition['name'].lower().replace('-', '') == transition_name.lower().replace('-', ''):
        transition_id = transition['id']
        break

    if not transition_id:
      raise Exception(f"Transition '{transition_name}' not found for JIRA ticket {issue_key}.")

    payload = {
      'transition': {
        'id': str(transition_id)
      }
    }

    required_fields = _get_required_fields_for_transition(issue_key, transition_name)
    fields = {}
    logging.info(f'Required fields for transition {transition_name} on JIRA ticket {issue_key}: {json.dumps(required_fields, indent=2)}')
    if required_fields:
      for field_name in required_fields:
        field_value = None
        if field_name == 'resolution':
          field_value = {'id': str(resolution_id)}
          if resolution_id:
            fields['resolution'] = field_value

    if fields:
      payload['fields'] = fields

    payload = json.dumps(payload)

    transition_response = requests.post(
      transition_url,
      data=payload,
      headers=headers,
      auth=auth
    )

    if transition_response.status_code == 204:
      logging.info(f'JIRA ticket {issue_key} transitioned to state {transition_name} successfully.')
      return f"JIRA ticket transitioned to {transition_name} successfully."
    else:
      logging.error(f'Failed to transition JIRA ticket {issue_key} to state {transition_name}. Status code: {transition_response.status_code}, Response: {transition_response.text}')
      raise Exception(f"Failed to transition JIRA ticket {issue_key} to state {transition_name}. Status code: {transition_response.status_code}, Response: {transition_response.text}")
  except Exception as e:
    logging.error(f'Failed to transition JIRA ticket {issue_key} to state {transition_name}. Error: {e}')
    raise e

def perform_jira_transition(
        issue_key: str,
        resolution_id: str,
        transition_name: str
) -> JiraIssueOutput:
  """
  Transitions a JIRA ticket to a specified state.

  Args:
      issue_key (str): The key of the JIRA issue to transition.
      transition_name (str): The name of the transition to perform.
      resolution_id (str, optional): The ID of the resolution to set when transitioning to a resolved state. Defaults to None.

  Returns:
      JiraIssueOutput: A message indicating the result of the transition.
  """
  try:
    result = _perform_jira_transition(issue_key, resolution_id, transition_name)
    return JiraIssueOutput(response=result)
  except Exception as e:
    return JiraIssueOutput(response=f"Failed to transition JIRA ticket to {transition_name}. Error: {str(e)}")