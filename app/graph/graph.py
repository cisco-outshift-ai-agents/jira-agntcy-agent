import logging
import uuid
from pydantic import BaseModel
from langgraph.checkpoint.memory import InMemorySaver
from core.config import Settings, get_settings_from_env
from supervisor_agent.supervisor_agent import SupervisorAgent


# Response from the JiraGraph
class JiraGraphResponse(BaseModel):
    """
    The output.
        Attributes:
        jira_output (str): output.
    """
    jira_output: str


class JiraGraph:
    def __init__(self, settings:Settings=None):
        """
        Initialize the JiraGraph as a LangGraph.
        """
        self.settings = settings or get_settings_from_env()
        self.graph = self.build_graph()

    def build_graph(self):
        """
        Build a LangGraph instance of the Jira graph.

        Returns:
            CompiledGraph: A compiled LangGraph instance.
        """
        graph = SupervisorAgent(settings=self.settings).agent()

        checkpointer = InMemorySaver()
        return graph.compile(checkpointer=checkpointer)

    def get_graph(self):
        return self.graph

    def serve(self, user_prompt: str):
        """
        Runs the LangGraph for Jira operations.

        Args:
            user_prompt str: user_prompt to serve.

        Returns:
            dict: Output data containing `jira_output`.
        """
        try:
            logging.info("Got user prompt: " + user_prompt)
            result = self.graph.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
            }, {"configurable": {"thread_id": uuid.uuid4()}})
            for m in result["messages"]:
                m.pretty_print()

            return result["messages"][-1].content, result

        except Exception as e:
            raise Exception("Jira operation failed: " + str(e))
