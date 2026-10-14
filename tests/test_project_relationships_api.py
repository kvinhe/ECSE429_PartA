"""Project relationships: /projects/:id/tasks and /projects/:id/categories."""
import api_client as api


def test_link_project_to_existing_todo():
    project, todo = api.create_project(), api.create_todo()
    assert api.post(f"/projects/{project['id']}/tasks", {"id": todo["id"]}).status_code == 201
    assert api.ids_of(api.get(f"/projects/{project['id']}/tasks"), "todos") == [todo["id"]]


def test_create_todo_directly_under_project():
    project = api.create_project()
    response = api.post(f"/projects/{project['id']}/tasks", {"title": "nested todo"})
    assert response.status_code == 201
    todo_id = response.json()["id"]
    assert todo_id in api.ids_of(api.get(f"/projects/{project['id']}/tasks"), "todos")


def test_project_with_no_tasks_returns_empty_list():
    project = api.create_project()
    assert api.get(f"/projects/{project['id']}/tasks").json() == {"todos": []}


def test_project_can_hold_several_tasks():
    project, first, second = api.create_project(), api.create_todo("a"), api.create_todo("b")
    api.link(f"/projects/{project['id']}/tasks", first["id"])
    api.link(f"/projects/{project['id']}/tasks", second["id"])
    assert api.ids_of(api.get(f"/projects/{project['id']}/tasks"), "todos") == sorted([first["id"], second["id"]])


def test_link_project_to_category():
    project, category = api.create_project(), api.create_category()
    assert api.post(f"/projects/{project['id']}/categories", {"id": category["id"]}).status_code == 201
    assert api.ids_of(api.get(f"/projects/{project['id']}/categories"), "categories") == [category["id"]]


def test_unlink_task_from_project_keeps_both_objects():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    assert api.delete(f"/projects/{project['id']}/tasks/{todo['id']}").status_code == 200
    assert api.get(f"/projects/{project['id']}/tasks").json() == {"todos": []}
    assert api.exists("todos", todo["id"])


def test_unlink_category_from_project():
    project, category = api.create_project(), api.create_category()
    api.link(f"/projects/{project['id']}/categories", category["id"])
    assert api.delete(f"/projects/{project['id']}/categories/{category['id']}").status_code == 200


def test_link_missing_todo_returns_404():
    project = api.create_project()
    assert api.post(f"/projects/{project['id']}/tasks", {"id": "987654"}).status_code == 404


def test_link_to_missing_project_returns_404():
    todo = api.create_todo()
    assert api.post("/projects/987654/tasks", {"id": todo["id"]}).status_code == 404


def test_create_task_under_project_without_title_returns_400():
    project = api.create_project()
    assert api.post(f"/projects/{project['id']}/tasks", {"description": "x"}).status_code == 400


def test_unlink_missing_task_returns_404():
    project, todo = api.create_project(), api.create_todo()
    assert api.delete(f"/projects/{project['id']}/tasks/{todo['id']}").status_code == 404


def test_project_relationship_collection_rejects_put_delete_patch():
    project = api.create_project()
    for method in ("PUT", "DELETE", "PATCH"):
        assert api.request(method, f"/projects/{project['id']}/tasks").status_code == 405


def test_deleting_project_removes_task_links_but_keeps_todos():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.delete(f"/projects/{project['id']}")
    assert api.get(f"/todos/{todo['id']}/tasksof").json() == {"projects": []}


def test_linking_task_leaves_other_projects_unchanged():
    project, other, todo = api.create_project(), api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    assert api.get(f"/projects/{other['id']}/tasks").json() == {"todos": []}
