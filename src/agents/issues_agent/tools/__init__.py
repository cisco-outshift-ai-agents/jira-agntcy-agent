from typing import Any, Callable, List
import os

from .issues import (
  create_jira_issue,
  assign_jira,
  update_issue_reporter,
  add_new_label_to_issue,
  get_jira_issue_details,
  _get_account_id_from_email,
  _create_jira_urlified_list,
)

from .transitions import (
  perform_jira_transition,
  get_jira_transitions
)

from .search import (
  search_jira_issues_using_jql
)

TOOLS: List[Callable[..., Any]] = [
  create_jira_issue,
  assign_jira,
  update_issue_reporter,
  add_new_label_to_issue,
  get_jira_issue_details,
  perform_jira_transition,
  get_jira_transitions,
  search_jira_issues_using_jql
]

TOOLS_A: List[Callable[..., Any]] = [
  create_jira_issue,
  assign_jira,
  update_issue_reporter,
]

TOOLS_B: List[Callable[..., Any]] = [
  add_new_label_to_issue,
  get_jira_issue_details,
  perform_jira_transition,
  get_jira_transitions,
  search_jira_issues_using_jql,
]

FINAL_TOOL = TOOLS_A if os.getenv("ENV") == "A" else TOOLS_B

__all__ = [
  "_get_account_id_from_email",
  "_create_jira_urlified_list",
]