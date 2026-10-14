"""Tests must fail, not skip, when the service is unreachable."""
import pytest
import requests
import api_client as api


def test_service_is_reachable():
    assert api.get("/todos").status_code == 200


def test_unreachable_service_raises_connection_error():
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get("http://localhost:1/todos", timeout=2)
