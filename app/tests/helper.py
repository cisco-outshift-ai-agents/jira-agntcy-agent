import os

def get_tools_executed(result):
  tools_executed = []
  tools_executed_dict = {}
  for message in result['messages']:
    if hasattr(message, 'tool_call_id'):
      if hasattr(message, 'name'):
        # print(f"\nTool: {message.name}, Content: {message.content}")
        tools_executed.append(message.name)
        tools_executed_dict[message.name] = message.content

  return tools_executed, tools_executed_dict

def verify_llm_settings_for_test():
  """
  Verifies that either OpenAI or Azure settings are set.

  Returns:
      bool: True if either OpenAI or Azure settings are set, False otherwise.
      str: Error message if neither settings are set.
  """
  print("DRYRUN: ", os.getenv("DRYRUN"))
  if not os.getenv("DRYRUN"):
    return False

  openai_settings = [
    os.getenv("TEST_OPENAI_ENDPOINT"),
    os.getenv("TEST_OPENAI_API_KEY"),
  ]

  azure_settings = [
    os.getenv("TEST_AZURE_OPENAI_ENDPOINT"),
    os.getenv("TEST_AZURE_OPENAI_API_KEY"),
    os.getenv("TEST_AZURE_OPENAI_API_VERSION")
  ]

  if all(openai_settings):
    return True, ""
  elif all(azure_settings):
    return True, ""
  else:
    return False, "Either OpenAI or Azure settings must be set."
