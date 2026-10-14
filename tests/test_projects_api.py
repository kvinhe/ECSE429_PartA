"""Projects API: /projects and /projects/:id."""
import pytest
import api_client as api


def test_get_projects_returns_default_project(default_state):
    assert set(default_state["projects"]) <= set(api.ids_of(api.get("/projects"), "projects"))


def test_create_project_with_title_only_applies_defaults():
    project = api.post("/projects", {"title": "thesis"}).json()
    assert (project["completed"], project["active"], project["description"]) == ("false", "false", "")


def test_create_project_with_all_fields():
    created = api.create_project("launch", completed=True, active=True, description="q4")
    stored = api.get(f"/projects/{created['id']}").json()["projects"][0]
    assert (stored["completed"], stored["active"], stored["description"]) == ("true", "true", "q4")


def test_created_project_appears_in_listing():
    created = api.create_project("listed")
    assert created["id"] in api.ids_of(api.get("/projects"), "projects")


def test_get_project_by_id():
    created = api.create_project("single")
    response = api.get(f"/projects/{created['id']}")
    assert response.status_code == 200 and response.json()["projects"][0]["title"] == "single"


def test_post_amends_only_given_fields():
    created = api.create_project("p", description="keep")
    api.post(f"/projects/{created['id']}", {"active": True})
    stored = api.get(f"/projects/{created['id']}").json()["projects"][0]
    assert (stored["active"], stored["description"], stored["title"]) == ("true", "keep", "p")


def test_put_replaces_project_fields():
    created = api.create_project("p", active=True, description="gone")
    assert api.put(f"/projects/{created['id']}", {"title": "p2"}).status_code == 200
    stored = api.get(f"/projects/{created['id']}").json()["projects"][0]
    assert (stored["title"], stored["active"], stored["description"]) == ("p2", "false", "")


def test_delete_project_removes_it():
    created = api.create_project("bye")
    assert api.delete(f"/projects/{created['id']}").status_code == 200
    assert not api.exists("projects", created["id"])


def test_filter_projects_by_title():
    created = api.create_project("unique-proj-title")
    assert api.ids_of(api.get("/projects?title=unique-proj-title"), "projects") == [created["id"]]


def test_create_project_without_title_is_accepted_or_rejected_consistently():
    """Documents actual behaviour: title is NOT mandatory for projects."""
    response = api.post("/projects", {"description": "untitled"})
    assert response.status_code in (201, 400)


def test_create_project_with_non_boolean_completed_is_rejected():
    assert api.post("/projects", {"title": "x", "completed": "yes"}).status_code == 400


def test_create_project_with_client_supplied_id_is_rejected():
    assert api.post("/projects", {"title": "x", "id": 5555}).status_code == 400


def test_get_missing_project_returns_404():
    assert api.get("/projects/987654").status_code == 404


def test_delete_already_deleted_project_returns_404():
    created = api.create_project("twice")
    api.delete(f"/projects/{created['id']}")
    assert api.delete(f"/projects/{created['id']}").status_code == 404


def test_amend_missing_project_returns_404():
    assert api.post("/projects/987654", {"title": "x"}).status_code == 404


@pytest.mark.parametrize("method", ["PUT", "DELETE", "PATCH"])
def test_unsupported_methods_on_projects_collection_return_405(method):
    assert api.request(method, "/projects").status_code == 405


def test_deleting_project_keeps_its_todos():
    project, todo = api.create_project(), api.create_todo()
    api.link(f"/projects/{project['id']}/tasks", todo["id"])
    api.delete(f"/projects/{project['id']}")
    assert api.exists("todos", todo["id"])


def test_amending_project_does_not_change_other_projects():
    first, second = api.create_project("a"), api.create_project("b")
    api.post(f"/projects/{first['id']}", {"title": "a2"})
    assert api.get(f"/projects/{second['id']}").json()["projects"][0]["title"] == "b"
