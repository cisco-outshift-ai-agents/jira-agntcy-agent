from pydantic import BaseModel


# response from a jira user tool
class JiraUserOutput(BaseModel):
    """
    The output.
        Attributes:
        response (str): detail response.
    """
    response: str


class GetJiraAccountIdByUserEmailInput(BaseModel):
    """
    The input for get Jira account ID by user email.
        Attributes:
        user_email (str): The email of the user.
    """
    user_email: str