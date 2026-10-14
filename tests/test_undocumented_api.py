"""Capabilities not described in the API docs: HEAD, OPTIONS, filtering, GUI, silent behaviours."""
import pytest
import api_client as api

COLLECTIONS = ["/todos", "/projects", "/categories"]


@pytest.mark.parametrize("path", COLLECTIONS)
def test_head_on_collection_returns_200_and_empty_body(path):
    response = api.head(path)
    assert response.status_code == 200 and response.content == b""


@pytest.mark.parametrize("path", COLLECTIONS)
def test_options_on_collection_lists_allowed_methods(path):
    allow = api.options(path).headers.get("Allow", "")
    assert {"GET", "POST", "HEAD", "OPTIONS"} <= set(m.strip() for m in allow.split(","))


def test_head_on_missing_object_returns_404():
    assert api.head("/todos/987654").status_code == 404


def test_head_on_existing_object_returns_200():
    todo = api.create_todo()
    assert api.head(f"/todos/{todo['id']}").status_code == 200


@pytest.mark.parametrize("path", ["/gui", "/gui/entities", "/docs"])
def test_html_pages_are_served(path):
    response = api.get(path)
    assert response.status_code == 200 and "html" in response.headers["Content-Type"]


def test_swagger_description_is_served_as_openapi_json():
    response = api.get("/docs/swagger")
    assert response.status_code == 200 and response.json()["openapi"].startswith("3.")


def test_unknown_filter_field_is_silently_ignored():
    """Actual behaviour: a filter on a field that does not exist returns everything."""
    everything = api.ids_of(api.get("/todos"), "todos")
    assert api.ids_of(api.get("/todos?nofield=1"), "todos") == everything


def test_filter_with_no_match_returns_empty_list():
    assert api.get("/todos?title=zzz-no-such-title").json() == {"todos": []}


def test_json_body_is_accepted_when_content_type_claims_xml():
    """Actual behaviour: the body is sniffed, the Content-Type header is not authoritative."""
    response = api.post("/todos", raw='{"title":"sniffed"}', content_type=api.XML)
    assert response.status_code == 201


def test_very_long_title_is_accepted_without_limit():
    response = api.post("/todos", {"title": "t" * 10000})
    assert response.status_code == 201 and len(response.json()["title"]) == 10000


def test_unicode_title_round_trips():
    todo = api.create_todo("日本語 – émoji ✅")
    assert api.get(f"/todos/{todo['id']}").json()["todos"][0]["title"] == "日本語 – émoji ✅"


def test_script_like_title_is_stored_verbatim():
    todo = api.create_todo("<script>alert(1)</script>")
    assert api.get(f"/todos/{todo['id']}").json()["todos"][0]["title"] == "<script>alert(1)</script>"


def test_unknown_route_returns_404():
    assert api.get("/nothing-here").status_code == 404
