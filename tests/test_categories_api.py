"""Categories API: /categories and /categories/:id."""
import pytest
import api_client as api


def test_get_categories_returns_default_categories(default_state):
    assert set(default_state["categories"]) <= set(api.ids_of(api.get("/categories"), "categories"))


def test_create_category_with_title_only():
    category = api.post("/categories", {"title": "errands"}).json()
    assert (category["title"], category["description"]) == ("errands", "")


def test_create_category_with_description():
    created = api.create_category("home", description="chores")
    assert api.get(f"/categories/{created['id']}").json()["categories"][0]["description"] == "chores"


def test_get_category_by_id():
    created = api.create_category("single")
    assert api.get(f"/categories/{created['id']}").json()["categories"][0]["title"] == "single"


def test_post_amends_category():
    created = api.create_category("c", description="keep")
    api.post(f"/categories/{created['id']}", {"title": "c2"})
    stored = api.get(f"/categories/{created['id']}").json()["categories"][0]
    assert (stored["title"], stored["description"]) == ("c2", "keep")


def test_put_replaces_category():
    created = api.create_category("c", description="gone")
    assert api.put(f"/categories/{created['id']}", {"title": "c2"}).status_code == 200
    assert api.get(f"/categories/{created['id']}").json()["categories"][0]["description"] == ""


def test_delete_category_removes_it():
    created = api.create_category("bye")
    assert api.delete(f"/categories/{created['id']}").status_code == 200
    assert not api.exists("categories", created["id"])


def test_filter_categories_by_title():
    created = api.create_category("unique-cat-title")
    assert api.ids_of(api.get("/categories?title=unique-cat-title"), "categories") == [created["id"]]


def test_create_category_without_title_is_rejected():
    response = api.post("/categories", {"description": "x"})
    assert response.status_code == 400


def test_create_category_with_empty_title_is_rejected():
    assert api.post("/categories", {"title": ""}).status_code == 400


def test_create_category_with_client_supplied_id_is_rejected():
    assert api.post("/categories", {"title": "x", "id": 4444}).status_code == 400


def test_get_missing_category_returns_404():
    assert api.get("/categories/987654").status_code == 404


def test_delete_already_deleted_category_returns_404():
    created = api.create_category("twice")
    api.delete(f"/categories/{created['id']}")
    assert api.delete(f"/categories/{created['id']}").status_code == 404


def test_amend_missing_category_returns_404():
    assert api.post("/categories/987654", {"title": "x"}).status_code == 404


@pytest.mark.parametrize("method", ["PUT", "DELETE", "PATCH"])
def test_unsupported_methods_on_categories_collection_return_405(method):
    assert api.request(method, "/categories").status_code == 405


def test_deleting_category_keeps_its_todos():
    category, todo = api.create_category(), api.create_todo()
    api.link(f"/categories/{category['id']}/todos", todo["id"])
    api.delete(f"/categories/{category['id']}")
    assert api.exists("todos", todo["id"])


def test_amending_category_does_not_change_siblings():
    first, second = api.create_category("a"), api.create_category("b")
    api.post(f"/categories/{first['id']}", {"title": "a2"})
    assert api.get(f"/categories/{second['id']}").json()["categories"][0]["title"] == "b"
