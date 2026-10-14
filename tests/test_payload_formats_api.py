"""JSON and XML payloads, including malformed payloads."""
import xml.etree.ElementTree as ElementTree
import pytest
import api_client as api

ENTITY_SAMPLES = {
    "todos": ("todo", "<todo><title>xml todo</title><description>d</description></todo>"),
    "projects": ("project", "<project><title>xml project</title></project>"),
    "categories": ("category", "<category><title>xml category</title></category>"),
}


@pytest.mark.parametrize("entity", ENTITY_SAMPLES)
def test_listing_can_be_returned_as_json(entity):
    response = api.get(f"/{entity}", accept=api.JSON)
    assert response.headers["Content-Type"].startswith(api.JSON)
    assert entity in response.json()


@pytest.mark.parametrize("entity", ENTITY_SAMPLES)
def test_listing_can_be_returned_as_xml(entity):
    response = api.get(f"/{entity}", accept=api.XML)
    assert response.headers["Content-Type"].startswith(api.XML)
    assert ElementTree.fromstring(response.text).tag == entity


@pytest.mark.parametrize("entity", ENTITY_SAMPLES)
def test_default_response_format_is_json(entity):
    assert api.get(f"/{entity}").headers["Content-Type"].startswith(api.JSON)


@pytest.mark.parametrize("entity", ENTITY_SAMPLES)
def test_object_can_be_created_from_xml_payload(entity):
    element_name, payload = ENTITY_SAMPLES[entity]
    response = api.post(f"/{entity}", raw=payload, content_type=api.XML, accept=api.XML)
    assert response.status_code == 201
    assert ElementTree.fromstring(response.text).tag == element_name
    created_id = ElementTree.fromstring(response.text).findtext("id")
    assert api.exists(entity, created_id)


def test_xml_created_todo_keeps_field_values():
    response = api.post("/todos", raw=ENTITY_SAMPLES["todos"][1], content_type=api.XML, accept=api.XML)
    root = ElementTree.fromstring(response.text)
    assert (root.findtext("title"), root.findtext("description")) == ("xml todo", "d")


def test_single_object_can_be_read_as_xml():
    todo = api.create_todo("as xml")
    root = ElementTree.fromstring(api.get(f"/todos/{todo['id']}", accept=api.XML).text)
    assert root.find("todo").findtext("title") == "as xml"


def test_malformed_json_returns_400_with_error_message():
    response = api.post("/todos", raw='{"title": "unterminated', content_type=api.JSON)
    assert response.status_code == 400
    assert response.json()["errorMessages"]


def test_malformed_json_creates_nothing(default_state):
    api.post("/todos", raw="{bad json", content_type=api.JSON)
    assert sorted(api.ids_of(api.get("/todos"), "todos")) == sorted(default_state["todos"])


def test_malformed_xml_returns_400_with_error_message():
    response = api.post("/todos", raw="<todo><title>oops</todo>", content_type=api.XML)
    assert response.status_code == 400
    assert response.json()["errorMessages"]


def test_malformed_xml_creates_nothing(default_state):
    api.post("/todos", raw="<todo><title>x", content_type=api.XML)
    assert sorted(api.ids_of(api.get("/todos"), "todos")) == sorted(default_state["todos"])


def test_empty_body_returns_400():
    assert api.post("/todos", raw="", content_type=api.JSON).status_code == 400


def test_plain_text_body_returns_400():
    assert api.post("/todos", raw="title=abc", content_type="text/plain").status_code == 400


def test_json_array_body_is_rejected():
    assert api.post("/todos", raw='[{"title":"x"}]', content_type=api.JSON).status_code == 400


def test_xml_wrapped_in_plural_root_is_rejected():
    payload = "<todos><todo><title>x</title></todo></todos>"
    assert api.post("/todos", raw=payload, content_type=api.XML).status_code == 400
