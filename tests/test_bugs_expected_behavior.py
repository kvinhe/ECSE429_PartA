"""EXPECTED (documented/reasonable) behaviour that the application does NOT meet.

Each test is marked xfail(strict=True): it is reported as 'xfailed' while the bug
exists and turns red (XPASS) the day the bug is fixed.  Run with --runxfail to see
the raw failures.  Paired with test_bugs_actual_behavior.py.
"""
import pytest
import api_client as api

bug = lambda ident, why: pytest.mark.xfail(strict=True, raises=AssertionError, reason=f"{ident}: {why}")


@bug("BUG-01", "todo->category link not visible from category side")
def test_category_lists_todo_linked_from_todo_side():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    assert api.ids_of(api.get(f"/categories/{category['id']}/todos"), "todos") == [todo["id"]]


@bug("BUG-02", "category->todo link not visible from todo side")
def test_todo_lists_category_linked_from_category_side():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/categories/{category['id']}/todos", todo["id"])
    assert api.ids_of(api.get(f"/todos/{todo['id']}/categories"), "categories") == [category["id"]]


@bug("BUG-03", "project->category link not visible from category side")
def test_category_lists_project_linked_from_project_side():
    project, category = api.create_project(), api.create_category()
    api.link(f"/projects/{project['id']}/categories", category["id"])
    assert api.ids_of(api.get(f"/categories/{category['id']}/projects"), "projects") == [project["id"]]


@bug("BUG-04", "GET relationship of a missing parent should be 404")
@pytest.mark.parametrize("path", ["/todos/987654/categories", "/projects/987654/tasks", "/todos/987654/tasksof"])
def test_relationship_of_missing_parent_returns_404(path):
    assert api.get(path).status_code == 404


@bug("BUG-05", "PUT documented as 'fields to amend' but title is mandatory")
def test_put_todo_with_only_description_succeeds():
    todo = api.create_todo("keep title")
    assert api.put(f"/todos/{todo['id']}", {"description": "only"}).status_code == 200


@bug("BUG-06", "doneStatus is returned as a string but a string is refused on input")
def test_returned_done_status_can_be_sent_back():
    todo = api.create_todo("round trip", doneStatus=True)
    stored = api.get(f"/todos/{todo['id']}").json()["todos"][0]
    assert api.put(f"/todos/{todo['id']}", {"title": "x", "doneStatus": stored["doneStatus"]}).status_code == 200


@bug("BUG-07", "failed (400) creations should not consume ids")
def test_failed_creation_does_not_consume_an_id():
    first = int(api.create_todo("a")["id"])
    api.post("/todos", {"title": ""})
    api.post("/todos", {"title": "x", "doneStatus": "bad"})
    second = int(api.create_todo("b")["id"])
    assert second == first + 1


@bug("BUG-08", "GET on todos/:id/tasksof/:id documented as 405, returns 404")
def test_get_on_relationship_instance_returns_405():
    todo, project = api.create_todo(), api.create_project()
    api.link(f"/todos/{todo['id']}/tasksof", project["id"])
    assert api.get(f"/todos/{todo['id']}/tasksof/{project['id']}").status_code == 405


@bug("BUG-09", "PUT on a project silently drops its task relationships")
def test_put_project_keeps_task_relationships():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.put(f"/projects/{project['id']}", {"title": "renamed"})
    assert api.ids_of(api.get(f"/projects/{project['id']}/tasks"), "todos") == [todo["id"]]


@bug("BUG-10", "deleting a category leaves a ghost link on the todo")
def test_deleting_category_removes_it_from_todo_categories():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/todos/{todo['id']}/categories", category["id"])
    api.delete(f"/categories/{category['id']}")
    assert api.get(f"/todos/{todo['id']}/categories").json() == {"categories": []}


@bug("BUG-11", "deleting a todo leaves a ghost link on the category")
def test_deleting_todo_removes_it_from_category_todos():
    todo, category = api.create_todo(), api.create_category()
    api.link(f"/categories/{category['id']}/todos", todo["id"])
    api.delete(f"/todos/{todo['id']}")
    assert api.get(f"/categories/{category['id']}/todos").json() == {"todos": []}


@bug("BUG-12", "relationship creation fails when the id is sent as XML")
def test_xml_relationship_creation_succeeds():
    todo, category = api.create_todo(), api.create_category()
    payload = f"<category><id>{category['id']}</id></category>"
    assert api.post(f"/todos/{todo['id']}/categories", raw=payload, content_type=api.XML).status_code == 201
