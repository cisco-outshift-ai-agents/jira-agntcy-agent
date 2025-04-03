import sys
from typing import Literal
from enum import Enum
from langchain_community.agent_toolkits import FileManagementToolkit

### Graph States
class GraphState(Enum):
  SONAR_AGENT = sys.intern("sonar_agent")
  CODE_AGENT = sys.intern("code_agent")
  GITHUB_AGENT = sys.intern("github_agent")
  ARCHITECT_AGENT = sys.intern("architect_agent")
  FINISH = sys.intern("finish")


RouterNextActions = Literal[
  GraphState.SONAR_AGENT.value,
  GraphState.CODE_AGENT.value,
  GraphState.GITHUB_AGENT.value,
  GraphState.ARCHITECT_AGENT.value,
  GraphState.FINISH.value,
]

def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants have the final answer or deliverable,"
        " prefix your response with FINAL ANSWER so the team knows to stop."
        f"\n{suffix}"
    )

toolkit = FileManagementToolkit(
    root_dir=str('./tmp')
)  # If you don't provide a root_dir, operations will default to the current working directory