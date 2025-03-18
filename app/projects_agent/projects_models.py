from typing import Optional

from pydantic import BaseModel


# response from a jira projects tool
class JiraProjectOutput(BaseModel):
    """
    The output.
        Attributes:
        response (str): detail response.
    """
    response: str


class GetJiraProjectByNameInput(BaseModel):
    """
    The input for get/search Jira project by name.
    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get
    https://<your instance>.atlassian.net/rest/api/3/project/search?query={{ProjectName}}
        Attributes:
        name (str): The name of the project.
    """
    name: str


class CreateJiraProjectInput(BaseModel):
    """
    The input for creating a Jira project.
        Attributes:
        name (str): The name of the project.
        key (str): The key of the project.
        assignee_type:Optional[str] = "UNASSIGNED" : assignee type.
        projectTypeKey: Optional[str] = "software" : project type.
    """
    name: str
    key: str
    leadAccountId: str
    assignee_type: Optional[str] = "PROJECT_LEAD"
    projectTypeKey: Optional[str] = "software"
    description: Optional[str] = "This project was created by the Jira Agent."


class GetJiraProjectInput(BaseModel):
    """
    The input for get on a Jira project.
        Attributes:
        projectIdOrKey (str): The projectIdOrKey of the project.
    """
    projectIdOrKey: str
