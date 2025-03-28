from __future__ import annotations

import base64
import http
import logging
import os
from typing import Optional, Any

import requests
from fastapi import APIRouter, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from models.models import ErrorResponse

from core.config import INTERNAL_ERROR_MESSAGE
from pydantic import ValidationError, BaseModel, Field

from jira_client.config import AUTH_TYPE_BASIC


# todo below models to be moved to shared models repo or models.py
class JiraAuth(BaseModel):
    """Expected input format for jira auth."""
    auth_type: Optional[str] = AUTH_TYPE_BASIC  # Authentication type
    username: str = Field(..., description="JIRA username for basic auth")
    api_token: str = Field(..., description="JIRA api token")


class JiraAgentPolicyCreateInput(BaseModel):
    """Expected input format for policy create endpoint."""
    jira_instance: str = Field(..., description="The jira instance configuration. Eg:example.atlassian.net")
    jira_auth: JiraAuth = Field(..., description="The auth type and configuration")
    policy: Optional[str] = ""


class JiraAgentPolicyOutput(BaseModel):
    """output format for policy endpoints."""
    jira_instance: str
    jira_auth: JiraAuth
    policy: str


router = APIRouter(tags=["Policy"])
logger = logging.getLogger(__name__)  # This will be "app.api.routes.<name>"

if os.getenv("DRYRUN") == "true":
    POLICY_DIR = "tmp_test_policy"
    POLICY_FILE_NAME = "tmp_test_policy.json"
    logging.info(f"Running policy API in test mode with {POLICY_DIR}/{POLICY_FILE_NAME}")
else:
    POLICY_DIR = "."  # Directory to store the policy file
    POLICY_FILE_NAME = "policy.json"


@router.post(
    "/policy",
    response_model=Any,
    responses={
        "200": {"model": JiraAgentPolicyOutput},
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
    },
    tags=["Policy"],
)
async def policy_create(file: UploadFile = File(...)):
    """
    Create new policy or replace existing policy.
    """
    try:
        # Read the uploaded file
        contents = await file.read()

        # Validate the JSON data against the Pydantic model
        try:
            policy = JiraAgentPolicyCreateInput.model_validate_json(contents)

            is_valid, error = validate_jira_auth(policy.jira_instance, policy.jira_auth)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error,
                )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.errors(),
            )

        # Write the contents to disk
        policy_file = os.path.join(POLICY_DIR, POLICY_FILE_NAME)
        with open(policy_file, "wb") as f:
            f.write(contents)
            logging.info(f"Policy file written to: {policy_file}")

        # write jira-auth to store, so it can be read by jira_client

        response = JiraAgentPolicyOutput(
            jira_instance=policy.jira_instance,
            jira_auth=policy.jira_auth,
            policy=policy.policy if policy.policy else ""
        )
        return response

    except HTTPException as http_exc:
        # Log HTTP exceptions and re-raise them so that FastAPI can generate the appropriate response.
        logging.error("HTTP error during run processing: %s", http_exc.detail)
        raise http_exc

    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_ERROR_MESSAGE,
        )


@router.get(
    "/policy",
    response_model=Any,
    responses={
        "200": {"model": JiraAgentPolicyOutput},
        "400": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
        "500": {"model": ErrorResponse},
    },
    tags=["Policy"],
)
async def policy_get():
    """
    Get configured policy.
    """
    try:
        # Read the policy file
        policy_file = os.path.join(POLICY_DIR, POLICY_FILE_NAME)
        if not os.path.exists(policy_file):
            logging.info(f"Policy file not found: {policy_file}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy file not found. Please configure it using the /policy endpoint.",
            )

        with open(policy_file, "r") as f:
            contents = f.read()

        # Parse the JSON data
        try:
            policy = JiraAgentPolicyCreateInput.model_validate_json(contents)
            response = JiraAgentPolicyOutput(
                jira_instance=policy.jira_instance,
                jira_auth=policy.jira_auth,
                policy=policy.policy if policy.policy else ""
            )
            return response
        except ValidationError as e:
            logging.error(f"Error parsing policy file: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.errors(),
            )

    except HTTPException as http_exc:
        # Log HTTP exceptions and re-raise them so that FastAPI can generate the appropriate response.
        logging.error("HTTP error during run processing: %s", http_exc.detail)
        raise http_exc

    except Exception as e:
        logging.error(f"Error reading policy file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_ERROR_MESSAGE,
        )


@router.delete(
    "/policy",
    response_model=Any,
    responses={
        "200": {"model": Any},
        "500": {"model": ErrorResponse},
    },
    tags=["Policy"],
)
async def policy_delete():
    """
    Delete configured policy.
    """
    try:
        # Path to the policy file
        policy_file = os.path.join(POLICY_DIR, POLICY_FILE_NAME)

        # Check if the file exists
        if os.path.exists(policy_file):
            # Delete the file
            os.remove(policy_file)
            logging.info(f"Policy file deleted: {policy_file}")

            # reset jira-auth in store, so it is updated for jira_client

        else:
            logging.warning(f"Policy file not found: {policy_file}")

        return JSONResponse(content={"message": "Policy file deleted successfully"}, status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        # Log HTTP exceptions and re-raise them so that FastAPI can generate the appropriate response.
        logging.error("HTTP error during run processing: %s", http_exc.detail)
        raise http_exc

    except Exception as e:
        logging.error(f"Error deleting policy file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_ERROR_MESSAGE,
        )


def validate_jira_auth(jira_instance, auth: JiraAuth) -> tuple[bool, str]:
    if auth.auth_type == AUTH_TYPE_BASIC:
        basic_auth_token = base64.b64encode(
            f'{auth.username}:{auth.api_token}'.encode()).decode()
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic " + basic_auth_token
        }
        url = f"https://{jira_instance}/rest/auth/1/session"
        response = requests.request(
            "GET",
            headers=headers,
            url=url
        )
        if response.status_code == http.HTTPStatus.OK:
            return True, ""

        return False, f"Invalid Jira basic auth token:{response.text}, {response.status_code}"
    else:
        return False, f"Invalid Jira auth type. Supported types: {AUTH_TYPE_BASIC}"


def get_policyfile_policy():
    try:
        policy_file = os.path.join(POLICY_DIR, POLICY_FILE_NAME)
        if os.path.exists(policy_file):
            with open(policy_file, "r") as f:
                contents = f.read()
            policy = JiraAgentPolicyCreateInput.model_validate_json(contents)
            return policy.policy if policy.policy else None
    except Exception as e:
        logging.error(f"Error reading policy: {e}")

    return None
