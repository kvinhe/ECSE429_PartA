"""Todos API: /todos and /todos/:id (documented behaviour that works as documented)."""
import pytest
import api_client as api


def test_get_todos_returns_default_todos(default_state):
    response = api.get("/todos")
    assert response.status_code == 200
    assert set(default_state["todos"]) <= set(api.ids_of(response, "todos"))


def test_create_todo_with_title_only_applies_defaults():
    response = api.post("/todos", {"title": "buy milk"})
    assert response.status_code == 201
    todo = response.json()
    assert (todo["title"], todo["doneStatus"], todo["description"]) == ("buy milk", "false", "")


def test_create_todo_with_all_fields_persists_them():
    created = api.create_todo("write report", doneStatus=True, description="due friday")
    stored = api.get(f"/todos/{created['id']}").json()["todos"][0]
    assert stored["title"] == "write report"
    assert stored["doneStatus"] == "true"
    assert stored["description"] == "due friday"


def test_created_todo_appears_in_listing():
    created = api.create_todo("listed")
    assert created["id"] in api.ids_of(api.get("/todos"), "todos")


def test_get_todo_by_id_returns_only_that_todo():
    created = api.create_todo("single")
    response = api.get(f"/todos/{created['id']}")
    assert response.status_code == 200
    assert [t["id"] for t in response.json()["todos"]] == [created["id"]]


def test_post_amends_only_given_fields():
    created = api.create_todo("original", description="keep me")
    response = api.post(f"/todos/{created['id']}", {"title": "changed"})
    assert response.status_code == 200
    stored = api.get(f"/todos/{created['id']}").json()["todos"][0]
    assert (stored["title"], stored["description"]) == ("changed", "keep me")


def test_put_with_title_replaces_omitted_fields_with_defaults():
    created = api.create_todo("original", description="will be lost", doneStatus=True)
    response = api.put(f"/todos/{created['id']}", {"title": "replaced"})
    assert response.status_code == 200
    stored = api.get(f"/todos/{created['id']}").json()["todos"][0]
    assert (stored["description"], stored["doneStatus"]) == ("", "false")


def test_delete_todo_removes_it():
    created = api.create_todo("to delete")
    assert api.delete(f"/todos/{created['id']}").status_code == 200
    assert not api.exists("todos", created["id"])


def test_delete_todo_does_not_remove_other_todos(default_state):
    created = api.create_todo("to delete")
    api.delete(f"/todos/{created['id']}")
    assert set(default_state["todos"]) <= set(api.ids_of(api.get("/todos"), "todos"))


def test_filter_todos_by_title_returns_only_matches():
    created = api.create_todo("needle-xyz")
    api.create_todo("haystack")
    response = api.get("/todos?title=needle-xyz")
    assert api.ids_of(response, "todos") == [created["id"]]


def test_filter_todos_by_done_status():
    done = api.create_todo("done one", doneStatus=True)
    response = api.get("/todos?doneStatus=true")
    assert done["id"] in api.ids_of(response, "todos")
    assert all(t["doneStatus"] == "true" for t in response.json()["todos"])


# ---- invalid operations / error codes ----

def test_create_todo_without_title_is_rejected():
    response = api.post("/todos", {"description": "no title"})
    assert response.status_code == 400
    assert "title" in response.json()["errorMessages"][0]


def test_create_todo_with_empty_title_is_rejected():
    assert api.post("/todos", {"title": ""}).status_code == 400


def test_create_todo_with_non_boolean_done_status_is_rejected():
    assert api.post("/todos", {"title": "x", "doneStatus": "maybe"}).status_code == 400


def test_create_todo_with_client_supplied_id_is_rejected():
    assert api.post("/todos", {"title": "x", "id": 99999}).status_code == 400


def test_create_todo_with_unknown_field_is_rejected():
    response = api.post("/todos", {"title": "x", "colour": "red"})
    assert response.status_code == 400


def test_get_missing_todo_returns_404():
    assert api.get("/todos/987654").status_code == 404


def test_get_non_numeric_todo_id_returns_404():
    assert api.get("/todos/abc").status_code == 404


def test_delete_already_deleted_todo_returns_404():
    created = api.create_todo("twice")
    api.delete(f"/todos/{created['id']}")
    assert api.delete(f"/todos/{created['id']}").status_code == 404


def test_amend_missing_todo_returns_404():
    assert api.post("/todos/987654", {"title": "x"}).status_code == 404


def test_put_missing_todo_returns_404():
    assert api.put("/todos/987654", {"title": "x"}).status_code == 404


def test_put_cannot_change_todo_id():
    created = api.create_todo("fixed id")
    assert api.put(f"/todos/{created['id']}", {"id": "7777", "title": "x"}).status_code == 400


@pytest.mark.parametrize("method", ["put", "delete", "patch"])
def test_unsupported_methods_on_collection_return_405(method):
    assert api.request(method.upper(), "/todos").status_code == 405


def test_patch_on_single_todo_returns_405():
    created = api.create_todo("patch me")
    assert api.request("PATCH", f"/todos/{created['id']}").status_code == 405


# ---- side effects ----

def test_creating_todo_leaves_existing_objects_unchanged(default_state):
    api.create_todo("side effect check")
    after = api.get("/todos").json()["todos"]
    for todo in after:
        if todo["id"] in default_state["todos"]:
            assert todo["title"] == default_state["todos"][todo["id"]]["title"]


def test_amending_todo_does_not_touch_siblings():
    first, second = api.create_todo("first"), api.create_todo("second")
    api.post(f"/todos/{first['id']}", {"title": "first changed"})
    assert api.get(f"/todos/{second['id']}").json()["todos"][0]["title"] == "second"


def test_deleting_todo_does_not_delete_related_project_or_category():
    todo, project, category = api.create_todo(), api.create_project(), api.create_category()
    api.link(f"/todos/{todo['id']}/tasksof", project["id"])
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    api.delete(f"/todos/{todo['id']}")
    assert api.exists("projects", project["id"]) and api.exists("categories", category["id"])
