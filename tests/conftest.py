"""Shared fixtures: readiness check, state snapshot, restore, random ordering."""
import random
import pytest
import api_client as api

ENTITY_RELATIONSHIPS = {
    "todos": ("tasksof", "categories"),
    "projects": ("tasks", "categories"),
    "categories": ("todos", "projects"),
}
FIELDS = {
    "todos": ("title", "doneStatus", "description"),
    "projects": ("title", "completed", "active", "description"),
    "categories": ("title", "description"),
}


def pytest_addoption(parser):
    parser.addoption("--random-seed", type=int, default=None,
                     help="shuffle test order using this pseudo random seed")


def pytest_collection_modifyitems(config, items):
    seed = config.getoption("--random-seed")
    if seed is None:
        return
    random.Random(seed).shuffle(items)
    print(f"\n[random order] seed={seed}")


def pytest_report_header(config):
    return f"todo manager under test: {api.BASE_URL}"


def _snapshot():
    state = {}
    for entity, relationships in ENTITY_RELATIONSHIPS.items():
        response = api.get("/" + entity)
        assert response.status_code == 200, response.text
        objects = response.json()[entity]
        state[entity] = {o["id"]: _normalise(o, relationships) for o in objects}
    return state


def _normalise(obj, relationships):
    normalised = dict(obj)
    for name in relationships:
        normalised[name] = sorted(r["id"] for r in obj.get(name, []))
    return normalised


def _delete_objects_created_by_test(before, after):
    for entity in ENTITY_RELATIONSHIPS:
        for object_id in set(after[entity]) - set(before[entity]):
            api.delete(f"/{entity}/{object_id}")


def _restore_default_object(entity, object_id, original, current):
    for name in ENTITY_RELATIONSHIPS[entity]:
        for stale in set(current.get(name, [])) - set(original[name]):
            api.delete(f"/{entity}/{object_id}/{name}/{stale}")
        for missing in set(original[name]) - set(current.get(name, [])):
            api.post(f"/{entity}/{object_id}/{name}", {"id": missing})
    if any(original[f] != current.get(f) for f in FIELDS[entity]):
        fields = {f: original[f] for f in FIELDS[entity]}
        api.post(f"/{entity}/{object_id}", fields)


@pytest.fixture(autouse=True)
def system_ready_and_restored():
    """Fail when the service is down; snapshot before; restore after each test."""
    try:
        before = _snapshot()
    except Exception as error:
        pytest.fail(f"Todo manager is not running at {api.BASE_URL}: {error}")
    yield before
    after = _snapshot()
    _delete_objects_created_by_test(before, after)
    after = _snapshot()
    for entity, objects in before.items():
        for object_id, original in objects.items():
            if after[entity].get(object_id) != original and object_id in after[entity]:
                _restore_default_object(entity, object_id, original, after[entity][object_id])


@pytest.fixture
def default_state(system_ready_and_restored):
    return system_ready_and_restored
