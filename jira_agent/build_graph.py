from jira_agent.agents.supervisor_agent.supervisor_agent import SupervisorAgent
from langgraph.checkpoint.memory import InMemorySaver

from jira_agent.graph.graph import JiraGraph


# builds the JiraWorkflow for use with LangGraph Studio
def build_graph():
    """
     Build a LangGraph instance of the Jira workflow.
 
     Returns:
     CompiledGraph: A compiled LangGraph instance.
     """
    # graph = SupervisorAgent().agent()

    # checkpointer = InMemorySaver()
    # return graph.compile(checkpointer=checkpointer)

    jira_graph = JiraGraph()
    return jira_graph.get_graph()


graph = build_graph()
