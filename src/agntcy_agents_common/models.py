from typing import List, Literal

from pydantic import BaseModel
from pydantic.fields import Field
from globals import RouterNextActions


class ChatBotQuestion(BaseModel):
  chat_id: str
  question: str


class Feedback(BaseModel):
  type: str
  reason: str
  additionalFeedback: str
  timestamp: str
  message: str

class UserInputRequest(BaseModel):
  """An input that the user should provide for the agent to be able to take action."""

  field_name: str = Field(description="The name of the field that should be provided.")
  field_description: str = Field(
    description="A description of what this field represents and how it will be used.",
  )
  field_values: List[str] = Field(
    description="A list of possible values that the user can provide for this field.",
  )


class JarvisResponseMetadata(BaseModel):
  """Metadata about the response from Jarvis Agent."""

  user_input: bool = Field(description="Indicates if the response requires user input")
  input_fields: list[UserInputRequest]


class JarvisResponse(BaseModel):
  """Response from Jarvis Agent."""

  answer: str = Field(description="The response from the Jarvis Agent")
  metadata: JarvisResponseMetadata = Field(
    description="""Metadata about the response. Set user_input if the response has user input and \
corresponding and input fields""",
  )


class SupervisorAction(BaseModel):
  action: RouterNextActions = Field(description="The action you will take to service the user")


class K8sSupervisorAction(BaseModel):
  action: Literal["generate config", "kubectl", "container images", "git"] = Field(
    description="The action you will take to service the user"
  )
