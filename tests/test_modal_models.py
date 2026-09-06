import importlib

import openai

from ell.configurator import config
import ell.models.modal as modal_models


def test_endpoint_base_url_normalization():
    url = "https://ep.us-west.modal.direct"
    assert modal_models.endpoint_base_url(url) == url + "/v1"
    assert modal_models.endpoint_base_url(url + "/") == url + "/v1"
    assert modal_models.endpoint_base_url(url + "/v1") == url + "/v1"
    assert modal_models.endpoint_base_url(url + "/v1/") == url + "/v1"


def test_kimi_registered_without_client_when_token_missing(monkeypatch):
    monkeypatch.delenv("MODAL_PROXY_TOKEN", raising=False)
    importlib.reload(modal_models)
    assert modal_models.default_client is None
    assert config.registry[modal_models.KIMI_K3].default_client is None


def test_kimi_registered_with_proxy_token_client(monkeypatch):
    monkeypatch.setenv("MODAL_PROXY_TOKEN", "wk-test.ws-test")
    monkeypatch.delenv("MODAL_ENDPOINT_URL", raising=False)
    importlib.reload(modal_models)
    client = config.registry[modal_models.KIMI_K3].default_client
    assert isinstance(client, openai.Client)
    assert client.api_key == "wk-test.ws-test"
    assert str(client.base_url) == modal_models.DEFAULT_ENDPOINT_URL + "/v1/"
    assert config.autocommit_model == modal_models.KIMI_K3


def test_endpoint_url_override(monkeypatch):
    monkeypatch.setenv("MODAL_PROXY_TOKEN", "wk-test.ws-test")
    monkeypatch.setenv("MODAL_ENDPOINT_URL", "https://other.us-west.modal.direct/v1")
    importlib.reload(modal_models)
    client = config.registry[modal_models.KIMI_K3].default_client
    assert str(client.base_url) == "https://other.us-west.modal.direct/v1/"
