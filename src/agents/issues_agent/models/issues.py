from typing import Optional
from pydantic import BaseModel

class LLMResponseOutput(BaseModel):
  """
  The output for JIRA issues.

  Attributes:
      response (str): Detailed response.
  """
  response: str

class CreateJiraIssueInput(BaseModel):
  """
  The input for creating a Jira issue.

  Attributes:
      project_key (str): Jira Project Key.
      summary (str): The summary of the issue.
      description (str): The description of the issue.
      issue_type (Optional[str]): The type of the issue (e.g., "Bug", "Task").
      assignee_email (Optional[str]): The email of the assignee.
      reporter_email (Optional[str]): The email of the reporter.
  """
  project_key: str
  summary: str
  description: str
  issue_type: Optional[str] = "Task"
  reporter_email: Optional[str] = ""
  assignee_email: Optional[str] = ""

class GetJiraIssueInput(BaseModel):
  """
  The input for getting a JIRA issue.

  Attributes:
      issueIdOrKey (str): The ID or key of the issue.
  """
  issueIdOrKey: str