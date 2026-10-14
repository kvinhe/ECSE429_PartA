"""ACTUAL behaviour for each bug in test_bugs_expected_behavior.py (all pass today)."""
import api_client as api


def test_bug01_category_does_not_list_todo_linked_from_todo_side():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    assert api.get(f"/categories/{category['id']}/todos").json() == {"todos": []}
    assert api.ids_of(api.get(f"/todos/{todo['id']}/categories"), "categories") == [category["id"]]


def test_bug02_todo_does_not_list_category_linked_from_category_side():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/categories/{category['id']}/todos", todo["id"])
    assert api.get(f"/todos/{todo['id']}/categories").json() == {"categories": []}
    assert api.ids_of(api.get(f"/categories/{category['id']}/todos"), "todos") == [todo["id"]]


def test_bug03_category_does_not_list_project_linked_from_project_side():
    project, category = api.create_project(), api.create_category()
    api.link(f"/projects/{project['id']}/categories", category["id"])
    assert api.get(f"/categories/{category['id']}/projects").json() == {"projects": []}


def test_bug04_missing_parent_relationship_returns_200_with_unrelated_data():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    response = api.get("/todos/987654/categories")
    assert response.status_code == 200
    assert category["id"] in api.ids_of(response, "categories")


def test_bug05_put_with_only_description_is_rejected_for_missing_title():
    todo = api.create_todo("keep title")
    response = api.put(f"/todos/{todo['id']}", {"description": "only"})
    assert response.status_code == 400 and "title" in response.json()["errorMessages"][0]


def test_bug06_string_done_status_is_rejected_but_boolean_is_accepted():
    todo = api.create_todo("round trip")
    assert api.put(f"/todos/{todo['id']}", {"title": "x", "doneStatus": "true"}).status_code == 400
    assert api.put(f"/todos/{todo['id']}", {"title": "x", "doneStatus": True}).status_code == 200


def test_bug07_failed_creations_consume_ids():
    first = int(api.create_todo("a")["id"])
    api.post("/todos", {"title": ""})
    api.post("/todos", {"title": "x", "doneStatus": "bad"})
    assert int(api.create_todo("b")["id"]) > first + 1


def test_bug08_get_on_relationship_instance_returns_404():
    todo, project = api.create_todo(), api.create_project()
    api.link(f"/todos/{todo['id']}/tasksof", project["id"])
    assert api.get(f"/todos/{todo['id']}/tasksof/{project['id']}").status_code == 404


def test_bug09_put_project_drops_task_relationships():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.put(f"/projects/{project['id']}", {"title": "renamed"})
    assert api.get(f"/projects/{project['id']}/tasks").json() == {"todos": []}
    assert api.exists("todos", todo["id"])


def test_bug10_deleted_category_still_listed_on_todo():
    todo, category = api.create_todo(), api.create_category("ghost")
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    api.delete(f"/categories/{category['id']}")
    assert api.ids_of(api.get(f"/todos/{todo['id']}/categories"), "categories") == [category["id"]]
    assert not api.exists("categories", category["id"])


def test_bug11_deleted_todo_still_listed_on_category():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/categories/{category['id']}/todos", todo["id"])
    api.delete(f"/todos/{todo['id']}")
    assert api.ids_of(api.get(f"/categories/{category['id']}/todos"), "todos") == [todo["id"]]
    assert not api.exists("todos", todo["id"])


def test_bug12_xml_relationship_creation_returns_404_but_json_works():
    todo, category = api.create_todo(), api.create_category()
    payload = f"<category><id>{category['id']}</id></category>"
    assert api.post(f"/todos/{todo['id']}/categories", raw=payload, content_type=api.XML).status_code == 404
    assert api.post(f"/todos/{todo['id']}/categories", {"id": category["id"]}).status_code == 201
