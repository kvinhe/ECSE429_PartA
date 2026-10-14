"""Cross-entity workflows (todos x projects x categories)."""
import api_client as api


def test_todo_belongs_to_project_and_category_at_once():
    todo, project, category = api.create_todo(), api.create_project(), api.create_category()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    stored = api.get(f"/todos/{todo['id']}").json()["todos"][0]
    assert stored["tasksof"] == [{"id": project["id"]}]
    assert stored["categories"] == [{"id": category["id"]}]


def test_project_link_is_visible_from_both_sides():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    assert api.ids_of(api.get(f"/todos/{todo['id']}/tasksof"), "projects") == [project["id"]]


def test_todo_can_belong_to_two_projects():
    todo, first, second = api.create_todo(), api.create_project("a"), api.create_project("b")
    api.link(f"/projects/{first['id']}/tasks", todo["id"])
    api.link(f"/projects/{second['id']}/tasks", todo["id"])
    assert api.ids_of(api.get(f"/todos/{todo['id']}/tasksof"), "projects") == sorted([first["id"], second["id"]])


def test_deleting_todo_removes_it_from_project_task_list():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.delete(f"/todos/{todo['id']}")
    assert api.get(f"/projects/{project['id']}/tasks").json() == {"todos": []}


def test_deleting_project_does_not_delete_category_links_of_its_todos():
    project, todo, category = api.create_project(), api.create_todo(), api.create_category()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    api.delete(f"/projects/{project['id']}")
    assert api.ids_of(api.get(f"/todos/{todo['id']}/categories"), "categories") == [category["id"]]


def test_task_created_under_project_can_be_categorised():
    project, category = api.create_project(), api.create_category()
    task_id = api.post(f"/projects/{project['id']}/tasks", {"title": "nested"}).json()["id"]
    assert api.post(f"/todos/{task_id}/categories", {"id": category["id"]}).status_code == 201


def test_done_status_change_does_not_affect_project_completion():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.post(f"/todos/{todo['id']}", {"doneStatus": True})
    assert api.get(f"/projects/{project['id']}").json()["projects"][0]["completed"] == "false"


def test_amending_todo_title_keeps_all_relationships():
    todo, project, category = api.create_todo(), api.create_project(), api.create_category()
    api.link(f"/todos/{todo['id']}/tasksof", project["id"])
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    api.post(f"/todos/{todo['id']}", {"title": "renamed"})
    stored = api.get(f"/todos/{todo['id']}").json()["todos"][0]
    assert stored["tasksof"] and stored["categories"]
