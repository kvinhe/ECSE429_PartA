"""Category relationships: /categories/:id/todos and /categories/:id/projects."""
import api_client as api


def test_link_category_to_todo():
    category, todo = api.create_category(), api.create_todo()
    assert api.post(f"/categories/{category['id']}/todos", {"id": todo["id"]}).status_code == 201
    assert api.ids_of(api.get(f"/categories/{category['id']}/todos"), "todos") == [todo["id"]]


def test_link_category_to_project():
    category, project = api.create_category(), api.create_project()
    assert api.post(f"/categories/{category['id']}/projects", {"id": project["id"]}).status_code == 201
    assert api.ids_of(api.get(f"/categories/{category['id']}/projects"), "projects") == [project["id"]]


def test_category_without_links_returns_empty_lists():
    category = api.create_category()
    assert api.get(f"/categories/{category['id']}/todos").json() == {"todos": []}
    assert api.get(f"/categories/{category['id']}/projects").json() == {"projects": []}


def test_unlink_todo_from_category():
    category, todo = api.create_category(), api.create_todo()
    api.link(f"/categories/{category['id']}/todos", todo["id"])
    assert api.delete(f"/categories/{category['id']}/todos/{todo['id']}").status_code == 200
    assert api.get(f"/categories/{category['id']}/todos").json() == {"todos": []}
    assert api.exists("todos", todo["id"])


def test_unlink_project_from_category():
    category, project = api.create_category(), api.create_project()
    api.link(f"/categories/{category['id']}/projects", project["id"])
    assert api.delete(f"/categories/{category['id']}/projects/{project['id']}").status_code == 200
    assert api.exists("projects", project["id"])


def test_link_missing_todo_returns_404():
    category = api.create_category()
    assert api.post(f"/categories/{category['id']}/todos", {"id": "987654"}).status_code == 404


def test_link_to_missing_category_returns_404():
    todo = api.create_todo()
    assert api.post("/categories/987654/todos", {"id": todo["id"]}).status_code == 404


def test_unlink_missing_relationship_returns_404():
    category, todo = api.create_category(), api.create_todo()
    assert api.delete(f"/categories/{category['id']}/todos/{todo['id']}").status_code == 404


def test_link_with_empty_body_returns_400():
    category = api.create_category()
    assert api.post(f"/categories/{category['id']}/todos", {}).status_code == 400


def test_category_relationship_collection_rejects_put_delete_patch():
    category = api.create_category()
    for method in ("PUT", "DELETE", "PATCH"):
        assert api.request(method, f"/categories/{category['id']}/todos").status_code == 405


def test_deleting_category_keeps_linked_todo():
    category, todo = api.create_category(), api.create_todo()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    api.delete(f"/categories/{category['id']}")
    assert api.exists("todos", todo["id"])
