import pytest


def test_root_redirects_to_static_page(client):
    url = "/"

    response = client.get(url, follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    activity_name = "Chess Club"

    response = client.get("/activities")

    assert response.status_code == 200
    activity = response.json()[activity_name]
    assert activity["description"]
    assert activity["schedule"]
    assert activity["max_participants"] == 12
    assert "michael@mergington.edu" in activity["participants"]


def test_signup_adds_participant(client):
    activity_name = "Chess Club"
    email = "new@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    before = client.get("/activities").json()[activity_name]["participants"]

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert client.get("/activities").json()[activity_name]["participants"] == before


def test_unregister_removes_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_rejects_missing_participant(client):
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    before = client.get("/activities").json()[activity_name]["participants"]

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}
    assert client.get("/activities").json()[activity_name]["participants"] == before


@pytest.mark.parametrize("method,endpoint", [("post", "signup"), ("delete", "participants")])
def test_mutation_rejects_unknown_activity(client, method, endpoint):
    email = "student@mergington.edu"
    before = client.get("/activities").json()

    response = client.request(method, f"/activities/Unknown Activity/{endpoint}", params={"email": email})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert client.get("/activities").json() == before


@pytest.mark.parametrize("method,endpoint", [("post", "signup"), ("delete", "participants")])
def test_mutation_requires_email(client, method, endpoint):
    activity_name = "Chess Club"
    before = client.get("/activities").json()[activity_name]["participants"]

    response = client.request(method, f"/activities/{activity_name}/{endpoint}")

    assert response.status_code == 422
    assert client.get("/activities").json()[activity_name]["participants"] == before