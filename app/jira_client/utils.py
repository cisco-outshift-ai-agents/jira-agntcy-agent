def get_url_with_proper_scheme(url: str) -> str:
  if not url.startswith("https://"):
    url = "https://" + url
  return url

def is_jira_cloud_url(url: str) -> bool:
  return "atlassian.net" in url