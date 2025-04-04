import os
import logging
import asyncio


def dryrun_response(mock_response):
  def dryrun_response_decorator(func):
    async def dryrun_response_wrapper(*args, **kwargs):
      if os.getenv("DRYRUN") == "true":
        logging.info("Running in dry-run mode, returning mock data.")
        return mock_response
      return await func(*args, **kwargs)

    def sync_dryrun_response_wrapper(*args, **kwargs):
      if os.getenv("DRYRUN") == "true":
        logging.info("Running in dry-run mode, returning mock data.")
        return mock_response
      return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
      return dryrun_response_wrapper
    else:
      return sync_dryrun_response_wrapper

  return dryrun_response_decorator