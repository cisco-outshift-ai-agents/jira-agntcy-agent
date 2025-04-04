# SPDX-FileCopyrightText: Copyright (c) 2025 Cisco and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agntcy_agents_common.logging_config import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Start the FastAPI application using Uvicorn
import asyncio
from uvicorn import Config, Server

from graph.graph import JiraGraph
from agntcy_agents_common.config import get_settings_from_env
from agntcy_agents_common.logging_config import configure_logging
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
# from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from protocol.ap.api.routes import stateless_runs

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
    logging.info(f".env file loaded from {env_path}")
  else:
    logging.warning("No .env file found. Ensure environment variables are set.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  """
  Defines startup and shutdown logic for the FastAPI application.

  This function follows the `lifespan` approach, allowing resource initialization
  before the server starts and cleanup after it shuts down.

  Args:
      app (FastAPI): The FastAPI application instance.

  Yields:
      None: The application runs while `yield` is active.

  Behavior:
  - On startup: Logs a startup message.
  - On shutdown: Logs a shutdown message.
  - Can be extended to initialize resources (e.g., database connections).
  """
  logging.info("Starting Jira Agent...")

  # Example: Attach database connection to app state (if needed)
  # app.state.db = await init_db_connection()

  yield  # Application runs while 'yield' is in effect.

  logging.info("Application shutdown")

  # Example: Close database connection (if needed)
  # await app.state.db.close()


def custom_generate_unique_id(route: APIRoute) -> str:
  """
  Generates a unique identifier for API routes.

  Args:
      route (APIRoute): The FastAPI route object.

  Returns:
      str: A unique string identifier for the route.

  Behavior:
  - If the route has tags, the ID is formatted as `{tag}-{route_name}`.
  - If no tags exist, the route name is used as the ID.
  """
  if route.tags:
      return f"{route.tags[0]}-{route.name}"
  return route.name


def add_handlers(app: FastAPI) -> None:
  """
  Adds global route handlers to the FastAPI application.

  This function registers common endpoints, such as the root message
  and the favicon.

  Args:
      app (FastAPI): The FastAPI application instance.

  Returns:
      None
  """

  @app.get(
    "/",
    summary="Root endpoint",
    description="Returns a welcome message for the API.",
    tags=["General"],
  )
  async def root() -> dict:
    """
    Root endpoint that provides a welcome message.

    Returns:
        dict: A JSON response with a greeting message.
    """
    user_prompt = "create a project for my venture test-venture-1 with key TV1"
    #user_prompt = "get details for project with key TV1"
    result = JiraGraph().serve(user_prompt)
    print(result)
    # result to send back to the user as part of JiraAgentApiResponse
    # logging.info(result['messages'][-1].content)
    # below for debugging
    # for m in result["messages"]:
    #     m.pretty_print()

    return {"message": "Gateway of the App"}


def create_app() -> FastAPI:
  """
  Creates and configures the FastAPI application instance.

  This function sets up:
  - The API metadata (title, version, OpenAPI URL).
  - CORS middleware to allow cross-origin requests.
  - Route handlers for API endpoints.
  - A custom unique ID generator for API routes.

  Returns:
      FastAPI: The configured FastAPI application instance.
  """
  settings = get_settings_from_env()
  app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    version="0.1.0",
    description=settings.PROJECT_NAME,
    lifespan=lifespan,  # Use the new lifespan approach for startup/shutdown
  )

  add_handlers(app)
  app.include_router(stateless_runs.router, prefix=settings.API_V1_STR)

  # Set all CORS enabled origins
  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
  )

  return app


def main() -> None:
  """
  Entry point for running the FastAPI application.

  This function performs the following:
  - Configures logging globally.
  - Loads environment variables from a `.env` file.
  - Retrieves the port from environment variables (default: 8125).
  - Starts the Uvicorn server.

  Returns:
      None
  """
  configure_logging()  # Apply global logging settings

  logger = logging.getLogger("app")  # Default logger for main script
  logger.info("Starting FastAPI application...")

  # Load environment variables before starting the application
  load_environment_variables()

  # Determine port number from environment variables or use the default
  port = int(os.getenv("JIRA_AGENT_PORT", "8125"))

  config = Config(
    app=create_app(),
    host="0.0.0.0",
    port=port,
    log_level="info",
  )
  server = Server(config)

  if asyncio.get_event_loop().is_running():
    # If running inside an existing event loop
    asyncio.ensure_future(server.serve())
  else:
    asyncio.run(server.serve())

if __name__ == "__main__":
  main()
