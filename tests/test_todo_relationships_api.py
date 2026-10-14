"""Todo relationships: /todos/:id/tasksof and /todos/:id/categories."""
import api_client as api


def test_link_todo_to_project_via_tasksof():
    todo, project = api.create_todo(), api.create_project()
    response = api.post(f"/todos/{todo['id']}/tasksof", {"id": project["id"]})
    assert response.status_code == 201
    assert api.ids_of(api.get(f"/todos/{todo['id']}/tasksof"), "projects") == [project["id"]]


def test_link_todo_to_category():
    todo, category = api.create_todo(), api.create_category()
    assert api.post(f"/todos/{todo['id']}/categories", {"id": category["id"]}).status_code == 201
    assert api.ids_of(api.get(f"/todos/{todo['id']}/categories"), "categories") == [category["id"]]


def test_todo_with_no_categories_returns_empty_list():
    todo = api.create_todo()
    assert api.get(f"/todos/{todo['id']}/categories").json() == {"categories": []}


def test_todo_can_have_several_categories():
    todo = api.create_todo()
    first, second = api.create_category("a"), api.create_category("b")
    api.link(f"/todos/{todo['id']}/categories", first["id"])
    api.link(f"/todos/{todo['id']}/categories", second["id"])
    assert api.ids_of(api.get(f"/todos/{todo['id']}/categories"), "categories") == sorted([first["id"], second["id"]])


def test_unlink_todo_from_category_keeps_both_objects():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    assert api.delete(f"/todos/{todo['id']}/categories/{category['id']}").status_code == 200
    assert api.get(f"/todos/{todo['id']}/categories").json() == {"categories": []}
    assert api.exists("todos", todo["id"]) and api.exists("categories", category["id"])


def test_unlink_todo_from_project_keeps_both_objects():
    todo, project = api.create_todo(), api.create_project()
    api.link(f"/todos/{todo['id']}/tasksof", project["id"])
    assert api.delete(f"/todos/{todo['id']}/tasksof/{project['id']}").status_code == 200
    assert api.exists("todos", todo["id"]) and api.exists("projects", project["id"])


def test_link_to_missing_category_returns_404():
    todo = api.create_todo()
    assert api.post(f"/todos/{todo['id']}/categories", {"id": "987654"}).status_code == 404


def test_link_to_missing_todo_returns_404():
    category = api.create_category()
    assert api.post("/todos/987654/categories", {"id": category["id"]}).status_code == 404


def test_link_with_empty_body_returns_400():
    todo = api.create_todo()
    assert api.post(f"/todos/{todo['id']}/categories", {}).status_code == 400


def test_unlink_missing_relationship_returns_404():
    todo, category = api.create_todo(), api.create_category()
    assert api.delete(f"/todos/{todo['id']}/categories/{category['id']}").status_code == 404


def test_unlink_twice_returns_404_the_second_time():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    api.delete(f"/todos/{todo['id']}/categories/{category['id']}")
    assert api.delete(f"/todos/{todo['id']}/categories/{category['id']}").status_code == 404


def test_todo_relationship_collection_rejects_put_delete_patch():
    todo = api.create_todo()
    for method in ("PUT", "DELETE", "PATCH"):
        assert api.request(method, f"/todos/{todo['id']}/categories").status_code == 405


def test_linking_leaves_unrelated_todos_unchanged():
    todo, other, category = api.create_todo(), api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    assert api.get(f"/todos/{other['id']}/categories").json() == {"categories": []}


def test_deleting_todo_removes_its_links():
    todo, project = api.create_todo(), api.create_project()
    api.link(f"/todos/{todo['id']}/tasksof", project["id"])
    api.delete(f"/todos/{todo['id']}")
    assert api.get(f"/projects/{project['id']}/tasks").json() == {"todos": []}


def test_todo_json_lists_its_relationships():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    stored = api.get(f"/todos/{todo['id']}").json()["todos"][0]
    assert stored["categories"] == [{"id": category["id"]}]
