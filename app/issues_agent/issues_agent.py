from core.llm import get_llm
from langgraph.prebuilt import create_react_agent

from issues_agent.issues_models import JiraIssueOutput
from issues_agent.issues_tools import (
  create_jira_issue,
  assign_jira,
  update_issue_reporter,
  add_new_label_to_issue,
  get_jira_issue_details,
)
from issues_agent.transitions_tools import perform_jira_transition, get_jira_transitions
from issues_agent.search_tools import retrieve_multiple_jira_issues, search_jira_issues_using_jql

class IssuesAgent:
  def __init__(self):
    self.name = "jira_issues_agent"
    self.tools = [
      create_jira_issue,
      assign_jira,
      update_issue_reporter,
      add_new_label_to_issue,
      get_jira_issue_details,
      perform_jira_transition,
      get_jira_transitions,
      retrieve_multiple_jira_issues,
      search_jira_issues_using_jql,
    ]
    self.prompt = (
      "You are a helpful agent. Only use the tools available."
      "1. you can only handle issues\n"
      "2. **Issues**: An issue is a single unit of work within a project. Issues can be of different types such as bug, task, etc.\n"
      "3. Projects and epics are not issues. They are higher-level containers for issues."
    )

  def agent(self):
    agent = create_react_agent(
      name=self.name,
      model=get_llm(),
      tools=self.tools,
      prompt=self.prompt,
      response_format=JiraIssueOutput
    )
    return agent