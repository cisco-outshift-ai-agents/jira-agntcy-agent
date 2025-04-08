from langgraph_supervisor import create_supervisor

from agntcy_agents_common.config import Settings, get_settings_from_env
from agntcy_agents_common.llm import get_llm

from agents.projects_agent.agent import ProjectsAgent
from agents.issues_agent.agent import IssuesAgent

from .prompt import prompt

# SupervisorAgent acts as a router for the Jira agents.
class SupervisorAgent:

    def __init__(self, settings:Settings=None):
        self.settings = settings or get_settings_from_env()
        self.name = "jira_supervisor"
        self.tools = []
        self.agents = [ProjectsAgent(settings).agent(), IssuesAgent(settings).agent()]
        self.prompt = (prompt.format(additional_context=""))

    def agent(self, input_prompt=None):

        if input_prompt:
            prompt = self.prompt + " " + input_prompt
        else:
            prompt = self.prompt

        # returns a state graph
        graph = create_supervisor(
            supervisor_name=self.name,
            tools=self.tools,
            agents=self.agents,
            model=get_llm(self.settings),
            prompt=prompt,
            add_handoff_back_messages=True,
            output_mode="full_history",
        )

        return graph
