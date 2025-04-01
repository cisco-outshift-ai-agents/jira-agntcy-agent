from langgraph_supervisor import create_supervisor
from core.config import Settings, get_settings_from_env
from core.llm import get_llm
from issues_agent.search_tools import search_jira_issues_using_jql
from projects_agent.projects_agent import ProjectsAgent
from issues_agent.issues_agent import IssuesAgent

# SupervisorAgent acts as a router for the Jira agents.
class SupervisorAgent:

    def __init__(self, settings:Settings=None):
        self.settings = settings or get_settings_from_env()
        self.name = "jira_supervisor"
        self.tools = []
        self.agents = [ProjectsAgent(settings).agent(), IssuesAgent(settings).agent()]
        self.prompt = (
            "You are a team supervisor managing the provided Jira agents."
            "Only use the agents provided."
            "If an agent is not found, return an error message to the caller."
            "If an agent is found, return the agent response to the caller."
            "If the prompt is to assign a Jira issue to a user, use the issues agent directly."
            "Here is the hierarchy of Jira issue types and projects:\n"
            "1. **Projects**: A project is a collection of issues. Projects can be of different types such as software, business, etc.\n"
            "---\n"
            "Special instructions for Jira project-related operations:\n"
            "   - If user email is in the prompt instead of account id, pass it to the tool.\n"
            "2. **Issues**: Issues are the tasks or problems to be addressed within a project. They can be of different types such as Bug, Task, Story, Epic, and Sub-task.\n"
            "Issue agent will handle Jira transitions, issue creation, issue assignment, issue details, issue updates, and issue searches.\n"
            "Special instructions for Jira issue-related operations:\n"
            "   - When creating a Jira issue, if a project name is in the prompt, get the project info to obtain the project key. For operations like getting issue details or transitions, the project key is not needed.\n"
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
            model=get_llm(self.settings),
            prompt=prompt,
            add_handoff_back_messages=True,
            output_mode="full_history",
        )

        return graph
