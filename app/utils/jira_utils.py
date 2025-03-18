# common utils for jira operations
import logging
import os
from asyncio import Timeout
from urllib.error import HTTPError
import traceback
import requests
import json
from requests.exceptions import (ConnectionError, HTTPError, RequestException,
                                 Timeout)


def jira_request_get(url_path: str) -> str:
    try:
        # this will be read from in-memory store after being populated from customers policy file
        # TODO use from env variable until that is implemented
        jira_instance = os.getenv("JIRA_INSTANCE")
        jira_basic_auth_token = os.getenv("JIRA_BASIC_AUTH_TOKEN")

        headers = {
            "Accept": "application/json",
            "Authorization": "Basic " + jira_basic_auth_token
        }
        url = f"https://{jira_instance}{url_path}"
        logging.info(f"sending jira request to:{url}\n{headers}")
        response = requests.request(
            "GET",
            url,
            headers=headers,
        )
        response.raise_for_status()
        logging.info(f"got  jira response:{response}")

        resp = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
        return resp

    except (Timeout, ConnectionError) as conn_err:
        error_msg = {
            "error": "Connection timeout or failure",
            "exception": str(conn_err),
        }
        resp = json.dumps(error_msg)
        return resp

    except HTTPError as http_err:
        error_msg = {
            "error": "HTTP request failed",
            "exception": str(http_err),
        }
        resp = json.dumps(error_msg)
        return resp

    except RequestException as req_err:
        error_msg = {"error": "Request failed", "exception": str(req_err)}
        resp = json.dumps(error_msg)
        return resp

    except json.JSONDecodeError as json_err:
        error_msg = {"error": "Invalid JSON response", "exception": str(json_err)}
        resp = json.dumps(error_msg)
        return resp

    except Exception as e:
        error_msg = {
            "error": "Unexpected failure",
            "exception": str(e),
            "stack_trace": traceback.format_exc(),
        }
        resp = json.dumps(error_msg)
        return resp


def jira_request_post(url_path: str, payload) -> str:
    try:
        # this will be read from in-memory store after being populated from customers policy file
        # TODO use from env variable until that is implemented
        jira_instance = os.getenv("JIRA_INSTANCE")
        jira_basic_auth_token = os.getenv("JIRA_BASIC_AUTH_TOKEN")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Basic " + jira_basic_auth_token
        }
        url = f"https://{jira_instance}{url_path}"

        logging.info(f"sending jira request to:{url}, headers:{headers}, payload:{payload}")
        response = requests.request(
            "POST",
            url,
            data = payload,
            headers=headers,
        )
        response.raise_for_status()
        logging.info(f"got  jira response:{response}")

        resp = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
        return resp

    except (Timeout, ConnectionError) as conn_err:
        error_msg = {
            "error": "Connection timeout or failure",
            "exception": str(conn_err),
        }
        resp = json.dumps(error_msg)
        return resp

    except HTTPError as http_err:
        error_msg = {
            "error": "HTTP request failed",
            "exception": str(http_err),
        }
        resp = json.dumps(error_msg)
        return resp

    except RequestException as req_err:
        error_msg = {"error": "Request failed", "exception": str(req_err)}
        resp = json.dumps(error_msg)
        return resp

    except json.JSONDecodeError as json_err:
        error_msg = {"error": "Invalid JSON response", "exception": str(json_err)}
        resp = json.dumps(error_msg)
        return resp

    except Exception as e:
        error_msg = {
            "error": "Unexpected failure",
            "exception": str(e),
            "stack_trace": traceback.format_exc(),
        }
        resp = json.dumps(error_msg)
        return resp
