from jira import JIRA
from requests.auth import HTTPBasicAuth
from .config import JiraClientConfig, AUTH_TYPE_BASIC, AUTH_TYPE_TOKEN, AUTH_TYPE_OAUTH
import threading
import os
from .utils import is_jira_cloud_url, get_url_with_proper_scheme

class JiraClient:
  _client = None
  _lock = threading.Lock()

  def __init__(self, config: JiraClientConfig | None = None):
    config = config or JiraClientConfig.from_env()
    if not config.url:
      raise ValueError("JIRA URL is required")

    if is_jira_cloud_url(config.url):
      config.url = get_url_with_proper_scheme(config.url)

    if config.auth_type.lower() == AUTH_TYPE_BASIC:
      if not config.username or not config.api_token:
        raise ValueError("Username and API token are required for basic authentication")
      self.client = JIRA(server=config.url, basic_auth=(config.username, config.api_token))

    elif config.auth_type.lower() == AUTH_TYPE_TOKEN:
      if not config.username or not config.personal_access_token:
        raise ValueError("Username and personal access token are required for token authentication")
      self.client = JIRA(server=config.url, token_auth=config.personal_access_token)

    elif config.auth_type.lower() == AUTH_TYPE_OAUTH:
      if not config.oauth_credentials:
        raise ValueError("OAuth credentials are required for OAuth authentication")
      self.client = JIRA(server=config.url, oauth=config.oauth_credentials)

    else:
      raise ValueError("Unsupported authentication type. Use 'basic', 'token', or 'oauth'.")

  @classmethod
  def get_jira_instance(cls):
    if cls._client is None:
      with cls._lock:
        if cls._client is None:
          config = JiraClientConfig.from_env()
          cls._client = JiraClient(config).client
    return cls._client


class JiraRESTClient:
  _jira_instance = None
  _auth_instance = None
  _jira_server_url = None
  _jira_headers =   headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
  _lock = threading.Lock()

  @classmethod
  def get_auth_instance(cls):
    if cls._auth_instance is None:
      user_email = os.getenv('JIRA_USERNAME')
      access_token = os.getenv('JIRA_API_TOKEN')

      cls._auth_instance = HTTPBasicAuth(user_email, access_token)
    if cls._jira_server_url is None:
      cls._jira_server_url = os.getenv("JIRA_INSTANCE") or os.getenv('JIRA_URL')

      if is_jira_cloud_url(cls._jira_server_url):
        cls._jira_server_url = get_url_with_proper_scheme(cls._jira_server_url)

    return cls._jira_server_url, cls._auth_instance, cls._jira_headers
