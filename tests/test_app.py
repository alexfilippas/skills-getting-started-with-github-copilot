import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_map(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Programming Class" in payload
    assert "participants" in payload["Programming Class"]


def test_signup_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post(f"/activities/Programming%20Class/signup?email={email}")

    assert response.status_code == 200
    assert email in app_module.activities["Programming Class"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "emma@mergington.edu"

    response = client.post(f"/activities/Programming%20Class/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_rejects_unknown_activity(client):
    response = client.post("/activities/Unknown%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "temp.student@mergington.edu"
    app_module.activities["Gym Class"]["participants"].append(email)

    response = client.delete(f"/activities/Gym%20Class/participants?email={email}")

    assert response.status_code == 200
    assert email not in app_module.activities["Gym Class"]["participants"]


def test_unregister_rejects_missing_participant(client):
    response = client.delete("/activities/Gym%20Class/participants?email=missing@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_rejects_unknown_activity(client):
    response = client.delete("/activities/Unknown%20Club/participants?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
