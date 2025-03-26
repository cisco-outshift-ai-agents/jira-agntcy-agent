import json
import logging
import os

from users_agent.users_models import JiraUserOutput
from users_agent.users_models import GetJiraAccountIdByUserEmailInput

from utils.jira_utils import jira_request_get, jira_request_post
from utils.dryrun_utils import dryrun_response

from core.config import INTERNAL_ERROR_MESSAGE


# option 1-if using the users_agent to get_jira_accountID_by_user_email, add this to the supervisor prompt under projects section.
# "The project lead Account ID must be obtained by using the user email supplied at project creation and the available agents."
# "The user email supplied at project creation is not the project lead Account ID\n"
# option 2-adding get_jira_accountID_by_user_email to the supervisor tools also works, without adding users agent to supervisor agents
# option 3- used currently - helper fn _get_jira_accountID_by_user_email invoked from project agent tools as required.
@dryrun_response("test")
def get_jira_accountID_by_user_email(input: GetJiraAccountIdByUserEmailInput) -> JiraUserOutput:
    """get jira user account ID by user email.
         Args:
         input (GetJiraAccountIdByUserEmailInput):
             The user-provided input that guides the jira account ID retrieval.
             This request is serialized from a `GetJiraAccountIdByUserEmailInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         JiraUserOutput:
             A JSON representation of the JiraUserOutput.
             This response is serialized from a `JiraUserOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    try:
        logging.info(f"tool input:{input}")
        if not input or input is None:
            return JiraUserOutput(response="error performing the operation")

        url_path = f"/rest/api/3/groupuserpicker?query=" + input.user_email
        jira_resp = jira_request_get(url_path)
        user_data = json.loads(jira_resp)

        # Extract accountId from the response
        account_id = None
        if 'users' in user_data and 'users' in user_data['users']:
            for user in user_data['users']['users']:
                account_id = user['accountId']

        if account_id:
            response_str = f"{account_id} for user email: {input.user_email}"
        else:
            response_str = f"Could not find Jira account ID for user email: {input.user_email}, user details: {jira_resp}"

        resp = JiraUserOutput(response=response_str)
        logging.info(f"tool output:{resp}")

    except Exception as e:
        response_str = INTERNAL_ERROR_MESSAGE + ":" + str(e)
        resp = JiraUserOutput(response=response_str)

    return resp
