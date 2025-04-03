from langgraph.prebuilt import create_react_agent

from agntcy_agents_common.llm import get_llm
from agntcy_agents_common.config import get_settings_from_env

from .models import LLMResponseOutput
from .tools import TOOLS
from .prompt import prompt

class IssuesAgent:
  def __init__(self, settings=None):
    self.settings = settings or get_settings_from_env()
    self.name = "jira_issues_agent"
    self.tools = TOOLS
    self.prompt = prompt.format(additional_context="")

  def agent(self):
    agent = create_react_agent(
      name=self.name,
      model=get_llm(self.settings),
      tools=self.tools,
      prompt=self.prompt,
      response_format=LLMResponseOutput
    )
    return agent