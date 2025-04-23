import json
import logging

from dotenv import load_dotenv, find_dotenv
from httpx_sse import ServerSentEvent

import os
import asyncio
from agntcy_acp import AsyncACPClient, ApiClientConfiguration
from agntcy_acp.acp_v0.async_client.api_client import ApiClient as AsyncApiClient

from agntcy_acp.models import (
    RunCreateStateless,
    RunResult,
    RunError,
    Config,
)

from clients.acp_client.logging_config import configure_logging

logger = configure_logging()


def load_environment_variables(env_file: str | None = None) -> None:
    """
    Load environment variables from a .env file safely.

    This function loads environment variables from a `.env` file, ensuring
    that critical configurations are set before the application starts.

    Args:
        env_file (str | None): Path to a specific `.env` file. If None,
                               it searches for a `.env` file automatically.

    Behavior:
    - If `env_file` is provided, it loads the specified file.
    - If `env_file` is not provided, it attempts to locate a `.env` file in the project directory.
    - Logs a warning if no `.env` file is found.

    Returns:
        None
    """
    env_path = env_file or find_dotenv()

    if env_path:
        load_dotenv(env_path, override=True)
        logger.info(f".env file loaded from {env_path}")
    else:
        logger.warning("No .env file found. Ensure environment variables are set.")


async def run_stateless(query, process_event):
    """
  Create a stateless run with the input spec from jarvis-agent.json and stream the output.
  Calls process_event(event, user_email) for each streamed event.
  """
    # Host can't have trailing slash
    client_config = ApiClientConfiguration(
        host=f"http://localhost:{os.environ['API_PORT']}", api_key={"x-api-key": os.environ["API_KEY"]}, retries=3
    )

    async with AsyncApiClient(client_config) as api_client:

        acp_client = AsyncACPClient(api_client)
        agent_id = os.environ["AGENT_ID"]

        # Compose input according to the input spec in jarvis-agent.json
        # input_obj = {"messages": [{"type": "human", "content": query}], "is_completed": False}
        input_obj = {"query": query}
        # Ensure all message types are valid
        # for message in input_obj["messages"]:
        #     if message["type"] not in ["human", "assistant", "ai", "tool"]:
        #         raise ValueError(f"Invalid message type: {message['type']}")
        run_create = RunCreateStateless(
            agent_id=agent_id,
            input=input_obj,
            config=Config(),
        )
        # Create the stateless run and stream its output
        run_output = await acp_client.create_and_wait_for_stateless_run_output(run_create)
        if run_output.output is None:
            raise Exception("Run output is None")
        actual_output = run_output.output.actual_instance
        if isinstance(actual_output, RunResult):
            run_result: RunResult = actual_output
        elif isinstance(actual_output, RunError):
            run_error: RunError = actual_output
            raise Exception(f"Run Failed: {run_error}")
        else:
            raise Exception(f"ACP Server returned a unsupported response: {run_output}")
        run_state = run_result.values  # type: ignore
        logging.info(run_state)
        if "messages" in run_state:
            for i, m in enumerate(run_state["messages"]):
                metadata = run_state.get("metadata", [{}] * len(run_state["messages"]))
                event = ServerSentEvent(
                    event="data", data=json.dumps({"answer": m["content"], "metadata": metadata[i]})
                )
                await process_event(query, event)  # run = await acp_client.create_stateless_run(run_create)
        # run_id = run.run_id
        # async for event in await acp_client.stream_stateless_run_output(run_id):
        #   process_event(event, user_email)


if __name__ == "__main__":
    load_environment_variables()


    async def process_event(chat_id, event):
        print(f"Chat ID: {chat_id}, Event: {event.event}, Data: {event.data}")


    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_stateless("get me details for project APT", process_event))
