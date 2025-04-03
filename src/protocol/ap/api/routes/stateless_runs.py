from __future__ import annotations

import logging
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from agntcy_agents_common.config import INTERNAL_ERROR_MESSAGE, get_settings_from_env
from models.models import Any, ErrorResponse, RunCreateStateless, Union

from graph.graph import JiraGraph


router = APIRouter(tags=["Stateless Runs"])
logger = logging.getLogger(__name__)  # This will be "app.api.routes.<name>"
graph = JiraGraph()


@router.post(
    "/runs",
    response_model=Any,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
def run_stateless_runs_post(body: RunCreateStateless) -> Union[Any, ErrorResponse]:
    """
    Create Background Run
    """

    try:
        # Extract assistant_id from the payload
        agent_id = body.agent_id
        logging.debug(f"Agent id: %s", agent_id)

        # Validate that the assistant_id is not empty.
        if not body.agent_id:
            msg = "agent_id is required and cannot be empty."
            logging.error(msg)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=msg,
            )

        # Retrieve the 'input' field and ensure it is a dictionary.
        input_field = body.input
        if not isinstance(input_field, dict):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Invalid input format"
            )

        # Retrieve the 'query' field from the input dictionary.
        query = input_field.get("query")
        logging.info("query: %s", query)
        result, result_detail = graph.serve(query)
        logging.info("result: %s", result)
    except HTTPException as http_exc:
        logger.error(
            "HTTP error during run processing: %s", http_exc.detail, exc_info=True
        )
        raise http_exc
    except Exception as exc:
        logger.error("Internal error during run processing: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_ERROR_MESSAGE,
        )

    payload = {
        "agent_id": agent_id,
        "output": result,
        "model": get_settings_from_env().OPENAI_API_VERSION,
        "metadata": {},
    }

    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


@router.post(
    "/runs/stream",
    response_model=str,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
def stream_run_stateless_runs_stream_post(
    body: RunCreateStateless,
) -> Union[str, ErrorResponse]:
    """
    Create Run, Stream Output
    """
    pass


@router.post(
    "/runs/wait",
    response_model=Any,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
def wait_run_stateless_runs_wait_post(
    body: RunCreateStateless,
) -> Union[Any, ErrorResponse]:
    """
    Create Run, Wait for Output
    """
    pass