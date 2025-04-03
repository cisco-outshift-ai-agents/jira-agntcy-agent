from agents.supervisor_agent.supervisor_agent import SupervisorAgent
from langgraph.checkpoint.memory import InMemorySaver

# To run the standalone LangGraph Server:
# % pip install --upgrade "langgraph-cli[inmem]"
# % langgraph dev

# Builds the graph for use with LangGraph Studio

def build_graph():
  """
  Constructs and compiles a LangGraph instance.

  This function initializes a `SupervisorAgent` to create the base graph structure
  and uses an `InMemorySaver` as the checkpointer for the compilation process.

  The resulting compiled graph can be used to execute Supervisor workflow in LangGraph Studio.

  Returns:
  CompiledGraph: A fully compiled LangGraph instance ready for execution.
  """
  graph = SupervisorAgent().agent()

  checkpointer = InMemorySaver()
  return graph.compile(checkpointer=checkpointer)
