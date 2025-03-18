from supervisor_agent.supervisor_agent import SupervisorAgent
from langgraph.checkpoint.memory import InMemorySaver

# To run the standalone JiraGraph in LangGraph Studio:
# (env) app % langgraph dev

# builds the JiraWorkflow for use with LangGraph Studio
def build_graph(self):
    """
    Build a LangGraph instance of the Jira workflow.

    Returns:
    CompiledGraph: A compiled LangGraph instance.
    """
    graph = SupervisorAgent().agent()

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)
