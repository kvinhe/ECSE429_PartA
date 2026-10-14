"""Thin HTTP client for the rest api todo list manager."""
import os
import requests

BASE_URL = os.environ.get("TODO_API_URL", "http://localhost:4567")
TIMEOUT_SECONDS = 10
JSON = "application/json"
XML = "application/xml"


def request(method, path, body=None, content_type=JSON, accept=None, raw=None, **kwargs):
    headers = {}
    if accept:
        headers["Accept"] = accept
    data = raw
    if body is not None:
        headers["Content-Type"] = JSON
        data = None
    elif raw is not None:
        headers["Content-Type"] = content_type
    return requests.request(
        method, BASE_URL + path,
        json=body, data=data, headers=headers,
        timeout=TIMEOUT_SECONDS, **kwargs)


def get(path, **kw): return request("GET", path, **kw)
def post(path, body=None, **kw): return request("POST", path, body, **kw)
def put(path, body=None, **kw): return request("PUT", path, body, **kw)
def delete(path, **kw): return request("DELETE", path, **kw)
def head(path, **kw): return request("HEAD", path, **kw)
def options(path, **kw): return request("OPTIONS", path, **kw)


def create(entity, **fields):
    """Create an object and return its JSON; fails loudly if creation fails."""
    response = post("/" + entity, fields)
    assert response.status_code == 201, response.text
    return response.json()


def create_todo(title="test todo", **fields): return create("todos", title=title, **fields)
def create_project(title="test project", **fields): return create("projects", title=title, **fields)
def create_category(title="test category", **fields): return create("categories", title=title, **fields)


def link(path, target_id):
    response = post(path, {"id": str(target_id)})
    assert response.status_code == 201, response.text


def ids_of(response, collection_key):
    return sorted(item["id"] for item in response.json()[collection_key])


def exists(entity, object_id):
    return get(f"/{entity}/{object_id}").status_code == 200
