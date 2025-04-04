# SPDX-FileCopyrightText: Copyright (c) 2025 Cisco and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Literal, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings

# Error messages
INTERNAL_ERROR_MESSAGE = "An unexpected error occurred"


class Settings(BaseSettings):
  # Application settings
  API_V1_STR: str = "/api/v1"
  ENVIRONMENT: Literal["local", "staging", "production"] = "local"
  PROJECT_NAME: str = "Jira Agent"
  DESCRIPTION: str = "Agent serving jira operations via natural language"

  # Jira configuration
  # registered Jira instance for this deployment
  JIRA_INSTANCE: str = None

  # Langchain settings (optional)
  LANGCHAIN_TRACING_V2: bool = False
  LANGCHAIN_ENDPOINT: Optional[str] = None
  LANGCHAIN_API_KEY: Optional[str] = None
  LANGCHAIN_PROJECT: Optional[str] = None
  LANGSMITH_API_KEY: Optional[str] = None

  # Mandatory LLM settings
  LLM_PROVIDER: Optional[str] = "azure"  # or "openai"
  OPENAI_TEMPERATURE: float = 0.7

  # Azure settings
  AZURE_OPENAI_ENDPOINT: Optional[str] = None
  AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = "gpt-4o"
  AZURE_OPENAI_API_KEY: Optional[str] = None
  AZURE_OPENAI_API_VERSION: Optional[str] = None

  # OpenAI settings
  OPENAI_ENDPOINT: Optional[str] = None
  OPENAI_API_KEY: Optional[str] = None
  OPENAI_API_VERSION: Optional[str] = "gpt-4o"

  # Validate LLM settings
  @model_validator(mode="after")
  def check_required_settings(self) -> "Settings":
      logger = logging.getLogger(__name__)
      logger.info("Running model validator for Settings...")
      # jira_instance = self.JIRA_INSTANCE.lower()
      # if not jira_instance:
      #     raise ValueError("Missing required JIRA_INSTANCE environment variable")

      provider = self.LLM_PROVIDER.lower()
      if provider == "azure":
          missing = []
          if not self.AZURE_OPENAI_ENDPOINT:
              missing.append("AZURE_OPENAI_ENDPOINT")
          if not self.AZURE_OPENAI_API_KEY:
              missing.append("AZURE_OPENAI_API_KEY")
          if not self.AZURE_OPENAI_API_VERSION:
              missing.append("AZURE_OPENAI_API_VERSION")
          if missing:
              raise ValueError(
                  f"Missing required Azure OpenAI environment variables: {', '.join(missing)}"
              )
      elif provider == "openai":
          missing = []
          if not self.OPENAI_ENDPOINT:
              missing.append("OPENAI_ENDPOINT")
          if not self.OPENAI_API_KEY:
              missing.append("OPENAI_API_KEY")
          if not self.OPENAI_API_VERSION:
              missing.append("OPENAI_API_VERSION")
          if missing:
              raise ValueError(
                  f"Missing required OpenAI environment variables: {', '.join(missing)}"
              )
      else:
          raise ValueError(f"Unsupported LLM provider: {provider}")
      return self

  class Config:
      env_file = ".env"
      extra = "ignore"  # This will ignore any extra environment variables.

def get_settings_from_env() -> Settings:
    return Settings()

