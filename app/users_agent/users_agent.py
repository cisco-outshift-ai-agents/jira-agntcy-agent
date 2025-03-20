from core.llm import get_llm

from langgraph.prebuilt import create_react_agent

from users_agent.users_models import JiraUserOutput

from users_agent.users_tools import get_jira_accountID_by_user_email


# NOT TO BE USED CURRENTLY
class UsersAgent:

    def __init__(self):
        self.name = "jira_users_agent"
        self.tools = [get_jira_accountID_by_user_email]
        self.prompt = ("You are a helpful agent. Only use the tools available."
                       "1. you can only handle users\n")

    def agent(self):
        agent = create_react_agent(
            name=self.name,
            model=get_llm(),
            tools=self.tools,
            prompt=self.prompt,
            response_format=JiraUserOutput
        )
        return agent
