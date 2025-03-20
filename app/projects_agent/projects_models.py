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
        leadAccountId: (str) : lead account ID.
        projectTypeKey: Optional[str] = "software" : project type.
        description: Optional[str] = "This project was created by the Jira Agent." : project description.
    """
    name: str
    key: str
    leadAccountId: str
    projectTypeKey: Optional[str] = "software"
    description: Optional[str] = "This project was created by the Jira Agent."


class UpdateJiraProjectDescriptionInput(BaseModel):
    """
    The input for updating a Jira project description.
        Attributes:
        key (str): The key of the project.
        description: (str) : description.
    """
    key: str
    description: str

class UpdateJiraProjectLeadInput(BaseModel):
    """
    The input for updating a Jira project lead.
        Attributes:
        key (str): The key of the project.
        leadAccountId: str : lead account ID. (Eg. 5b10a2844c20165700ede21g)
    """
    key: str
    leadAccountId: str
