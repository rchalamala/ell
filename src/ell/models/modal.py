"""
This module handles the registration of models served from a Modal Endpoint
within the ell framework.

Modal Endpoints (https://modal.com/docs/guide/endpoints) expose the OpenAI
Chat Completions API under ``<endpoint-url>/v1`` and authenticate with a
workspace proxy token passed as the bearer token, so the stock ``openai``
client is used with a custom ``base_url``.

Configuration is read from the environment:

* ``MODAL_PROXY_TOKEN_ID`` / ``MODAL_PROXY_TOKEN_SECRET`` -- the proxy token
  pair (``wk-…`` / ``ws-…``) as minted by ``modal workspace proxy-tokens create``,
  or ``MODAL_PROXY_TOKEN`` in the combined ``wk-<id>.ws-<secret>`` form. Without
  one of these no client is registered and the models below are left to the
  default client.
* ``MODAL_ENDPOINT_URL`` -- optional override of the endpoint base URL
  (with or without the trailing ``/v1``). Defaults to the Kimi K3 endpoint.
"""

import os
from ell.configurator import config
import openai

import logging

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT_URL = "https://modal-labs-rahul-dev--ep-kimi-k3-server.us-west.modal.direct"

KIMI_K3 = "moonshotai/Kimi-K3"


def register(client: openai.Client):
    """
    Register the models served by the Modal Endpoint with the provided client.

    Args:
        client (openai.Client): An OpenAI client pointed at the Modal Endpoint's
                                ``/v1`` base URL and authenticated with a proxy token.
    """
    for model_id in [KIMI_K3]:
        config.register_model(model_id, client)


def endpoint_base_url(endpoint_url: str) -> str:
    return endpoint_url.rstrip("/").removesuffix("/v1") + "/v1"


def proxy_token_from_env() -> str | None:
    token_id = os.environ.get("MODAL_PROXY_TOKEN_ID")
    token_secret = os.environ.get("MODAL_PROXY_TOKEN_SECRET")
    if token_id and token_secret:
        return f"{token_id}.{token_secret}"
    return os.environ.get("MODAL_PROXY_TOKEN") or None


default_client = None
try:
    proxy_token = proxy_token_from_env()
    if not proxy_token:
        raise openai.OpenAIError(
            "MODAL_PROXY_TOKEN_ID/MODAL_PROXY_TOKEN_SECRET (or MODAL_PROXY_TOKEN) not found in environment variables"
        )
    default_client = openai.Client(
        base_url=endpoint_base_url(os.environ.get("MODAL_ENDPOINT_URL") or DEFAULT_ENDPOINT_URL),
        api_key=proxy_token,
    )
except openai.OpenAIError as e:
    pass

register(default_client)
