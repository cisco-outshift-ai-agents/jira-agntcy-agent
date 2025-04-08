# jira/config.py
import os
from dataclasses import dataclass
from typing import Literal, Optional, Any, Dict

AUTH_TYPE_BASIC = "basic"
AUTH_TYPE_TOKEN = "token"
AUTH_TYPE_OAUTH = "oauth"

@dataclass
class JiraClientConfig:
  url: str  # Base URL for Jira
  auth_type: Literal["basic", "token", "oauth"]  # Authentication type
  username: Optional[str] = None  # Username for basic authentication
  api_token: Optional[str] = None  # API token for token authentication
  personal_access_token: Optional[str] = None  # Token for PAT bearer token authorization
  oauth_credentials: Optional[Dict[str, Any]] = None  # Dict of properties for OAuth authentication

  @classmethod
  def from_env(cls):
    url =  os.getenv("JIRA_INSTANCE") or os.getenv("JIRA_URL")
    if not url:
      raise ValueError("The environment variable 'JIRA_URL' is required but not set.")

    username = os.getenv("JIRA_USERNAME")
    api_token = os.getenv("JIRA_API_TOKEN")
    personal_access_token = os.getenv("JIRA_PERSONAL_ACCESS_TOKEN")
    oauth_credentials = {
      "access_token": os.getenv("JIRA_OAUTH_ACCESS_TOKEN"),
      "access_token_secret": os.getenv("JIRA_OAUTH_ACCESS_TOKEN_SECRET"),
      "consumer_key": os.getenv("JIRA_OAUTH_CONSUMER_KEY"),
      "key_cert": os.getenv("JIRA_OAUTH_KEY_CERT"),
      "signature_method": os.getenv("JIRA_OAUTH_SIGNATURE_METHOD", "oauthlib.oauth1.SIGNATURE_HMAC_SHA1")
    }

    # Determine authentication type based on available environment variables
    auth_type = os.getenv("JIRA_AUTH_TYPE", AUTH_TYPE_BASIC).lower()

    if auth_type == AUTH_TYPE_BASIC:
      if not username or not api_token:
        raise ValueError("Both 'JIRA_USERNAME' and 'JIRA_API_TOKEN' are required for basic authentication.")

    elif auth_type == AUTH_TYPE_TOKEN:
      if not personal_access_token:
        raise ValueError("'JIRA_PERSONAL_ACCESS_TOKEN' is required for token authentication.")

    elif auth_type == AUTH_TYPE_OAUTH:
      if not all(oauth_credentials.values()):
        raise ValueError("All OAuth credentials are required for OAuth authentication.")

    else:
      raise ValueError(f"Unsupported authentication type: '{auth_type}'. Supported types are 'basic', 'token', and 'oauth'.")

    return cls(
      url=url,
      auth_type=auth_type,
      username=username,
      api_token=api_token,
      personal_access_token=personal_access_token,
      oauth_credentials=oauth_credentials,
    )