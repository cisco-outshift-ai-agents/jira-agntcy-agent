from langgraph_supervisor import create_supervisor

from core.llm import get_llm
from projects_agent.projects_agent import ProjectsAgent
from issues_agent.issues_agent import IssuesAgent

# SupervisorAgent acts as a router for the Jira agents.
class SupervisorAgent:

    def __init__(self):
        self.name = "jira_supervisor"
        self.tools = []
        self.agents = [ProjectsAgent().agent(), IssuesAgent().agent()]
        self.prompt = (
            "You are a team supervisor managing the provided jira agents."
            "Only use the agents provided"
            "If an agent is not found, return error message to the caller."
            "If an agent is found, return the agent response to the caller."
            "If the prompt is to assign a jira issue to a user, use the issues agent directly."
            "Here is the hierarchy of Jira issue types and projects:\n"
            "1. **Projects**: A project is a collection of issues. Projects can be of different types such as software,"
            "business, etc. When creating an Jira issue, if a project name is in the prompt, get the project info to obtain the project key.\n"
            "2. **Issue Types**: Issues are the building blocks of a project."

        )

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
            model=get_llm(),
            prompt=prompt,
            add_handoff_back_messages=True,
            output_mode="full_history",
        )

        return graph
