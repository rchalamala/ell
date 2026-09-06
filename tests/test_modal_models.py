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


def _clear_proxy_env(monkeypatch):
    for name in ("MODAL_PROXY_TOKEN", "MODAL_PROXY_TOKEN_ID", "MODAL_PROXY_TOKEN_SECRET", "MODAL_ENDPOINT_URL"):
        monkeypatch.delenv(name, raising=False)


def test_kimi_registered_without_client_when_token_missing(monkeypatch):
    _clear_proxy_env(monkeypatch)
    importlib.reload(modal_models)
    assert modal_models.default_client is None
    assert config.registry[modal_models.KIMI_K3].default_client is None


def test_kimi_registered_with_proxy_token_pair(monkeypatch):
    _clear_proxy_env(monkeypatch)
    monkeypatch.setenv("MODAL_PROXY_TOKEN_ID", "wk-test")
    monkeypatch.setenv("MODAL_PROXY_TOKEN_SECRET", "ws-test")
    importlib.reload(modal_models)
    client = config.registry[modal_models.KIMI_K3].default_client
    assert isinstance(client, openai.Client)
    assert client.api_key == "wk-test.ws-test"
    assert str(client.base_url) == modal_models.DEFAULT_ENDPOINT_URL + "/v1/"
    assert config.autocommit_model == modal_models.KIMI_K3


def test_combined_proxy_token_fallback(monkeypatch):
    _clear_proxy_env(monkeypatch)
    monkeypatch.setenv("MODAL_PROXY_TOKEN", "wk-combined.ws-combined")
    importlib.reload(modal_models)
    assert config.registry[modal_models.KIMI_K3].default_client.api_key == "wk-combined.ws-combined"


def test_pair_takes_precedence_over_combined(monkeypatch):
    _clear_proxy_env(monkeypatch)
    monkeypatch.setenv("MODAL_PROXY_TOKEN", "wk-combined.ws-combined")
    monkeypatch.setenv("MODAL_PROXY_TOKEN_ID", "wk-pair")
    monkeypatch.setenv("MODAL_PROXY_TOKEN_SECRET", "ws-pair")
    assert modal_models.proxy_token_from_env() == "wk-pair.ws-pair"


def test_endpoint_url_override(monkeypatch):
    _clear_proxy_env(monkeypatch)
    monkeypatch.setenv("MODAL_PROXY_TOKEN", "wk-test.ws-test")
    monkeypatch.setenv("MODAL_ENDPOINT_URL", "https://other.us-west.modal.direct/v1")
    importlib.reload(modal_models)
    client = config.registry[modal_models.KIMI_K3].default_client
    assert str(client.base_url) == "https://other.us-west.modal.direct/v1/"
