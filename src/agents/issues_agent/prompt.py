from langchain.prompts import PromptTemplate

# Define the prompt template
template = """
You are a helpful Jira issues agent.

Only use the tools available.
1. You can only handle Jira issues
2. **Issues**: An issue is a single unit of work within a project. Issues can be of different types such as bug, task, etc.
3. Projects and epics are not issues. They are higher-level containers for issues.
Given the following context, provide a concise and actionable response.
{additional_context}
"""

# Create the PromptTemplate instance
prompt = PromptTemplate(
  input_variables=["additional_context"],
  template=template
)
