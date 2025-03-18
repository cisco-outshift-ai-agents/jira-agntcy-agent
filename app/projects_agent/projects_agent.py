from core.llm import get_llm

from langgraph.prebuilt import create_react_agent

from projects_agent.projects_models import JiraProjectOutput

from projects_agent.projects_tools import get_jira_project_by_name, create_jira_project


class ProjectsAgent:

    def __init__(self):
        self.name="jira_projects_agent"
        self.tools=[get_jira_project_by_name, create_jira_project]
        self.prompt=("You are a helpful agent. Only use the tools available."
                   "1. you can only handle projects\n"
                   "2. **Projects**: A project is a collection of issues. Projects can be of different types such as software, business, etc.\n"
                   "3. Epics and stories are not projects. They are issues under a project.")

    def agent(self):

        agent = create_react_agent(
            name=self.name,
            model=get_llm(),
            tools=self.tools,
            prompt=self.prompt,
            response_format=JiraProjectOutput
        )
        return agent
