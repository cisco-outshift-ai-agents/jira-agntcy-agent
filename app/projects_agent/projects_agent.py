from core.llm import get_llm

from langgraph.prebuilt import create_react_agent

from projects_agent.projects_models import JiraProjectOutput

from projects_agent.projects_tools import (get_jira_project_by_name,
                                           create_jira_project,
                                           update_jira_project_description,
                                           update_jira_project_lead)


class ProjectsAgent:

    def __init__(self):
        self.name="jira_projects_agent"
        self.tools=[get_jira_project_by_name,
                    create_jira_project,
                    update_jira_project_description,
                    update_jira_project_lead]
        self.prompt=("You are a helpful agent. Only use the tools available."
                   "1. You can only handle projects\n"
                   "2. **Projects**: A project is a collection of issues. "
                   "3. Epics and stories are not projects. They are issues under a project."
                   "4. **ProjectTypeKey** or **Project Type** indicates the type of project such as software, business, etc.\n" 
                   "5. Always check if the project exists using the provided tools before creating it. New projects must be created only if they do not exist.\n"
                   "6. Always check if the project exists using the provided tools before updating it. Only existing projects must be updated\n")

    def agent(self):

        agent = create_react_agent(
            name=self.name,
            model=get_llm(),
            tools=self.tools,
            prompt=self.prompt,
            response_format=JiraProjectOutput
        )
        return agent
