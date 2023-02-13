import asyncio
import logging
from functools import wraps
from math import ceil, log2
from random import random
from openai import APIError
from openai.error import (
    APIConnectionError,
    AuthenticationError,
    InvalidRequestError,
    OpenAIError,
    RateLimitError,
    ServiceUnavailableError,
    TryAgain,
)
# from src.concurrent.asynchronous import run_async_tasks


logger = logging.getLogger(__name__)


OPENAI_MAX_RETRY = 10
# quota is reset in every 60 seconds
OPENAI_REFRESH_QUOTA = 60
OPENAI_EXP_CAP = int(ceil(log2(OPENAI_REFRESH_QUOTA)))


class OpenAINetworkManager:
    def __init__(self):
        raise AssertionError(f"{type(self).__name__} should not be instantiated.")

    @staticmethod
    def async_retry_with_exp_backoff(task):
        @wraps(task)
        def wrapper(*args, **kwargs):
            for i in range(OPENAI_MAX_RETRY + 1):
                wait_time = (1 << min(i, OPENAI_EXP_CAP)) + random() / 10
                try:
                    return task(*args, **kwargs)
                except (
                    RateLimitError,
                    ServiceUnavailableError,
                    APIConnectionError,
                    APIError,
                    TryAgain,
                ) as e:
                    if i == OPENAI_MAX_RETRY:
                        logger.error(
                            f"Retry, TooManyRequests or Server Error. {str(e)}"
                        )
                        raise e
                    else:
                        logger.warning(
                            f"Waiting {round(wait_time, 2)} seconds for API...",
                        )
                        sleep(wait_time)
                except AuthenticationError as e:
                    # No way to handle
                    logger.error(f"AuthenticationError: {str(e)}")
                    raise Exception(
                        "AuthenticationError: Incorrect API key is provided.",
                    )
                except InvalidRequestError as e:
                    logger.error(f"InvalidRequestError: {str(e)}")
                    raise e
                except OpenAIError as e:
                    logger.error(f"API Request failed. {str(e)}")
                    raise e
                except Exception as e:
                    logger.error(f"Error unrelated to API. {str(e)}")
                    raise e

        return wrapper


def interact_with_api(func, *args, **kwargs):
    @OpenAINetworkManager.async_retry_with_exp_backoff
    def interact():
        return func(*args, **kwargs)

    return interact()
