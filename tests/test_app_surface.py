"""
Smoke tests for app wiring and documented API surface (no database required).

Run: pip install -e ".[dev]" && pytest
"""

from fastapi.testclient import TestClient

from app.main import app

# Paths expected from routers in app/main.py and v1 endpoints (method + path template)
EXPECTED_ROUTE_METHODS = {
    ("GET", "/"),
    # auth
    ("GET", "/api/v1/auth/me"),
    ("POST", "/api/v1/auth/register"),
    ("POST", "/api/v1/auth/login"),
    # workspaces
    ("GET", "/api/v1/workspaces"),
    ("GET", "/api/v1/workspaces/my"),
    ("GET", "/api/v1/workspaces/slug/{slug}"),
    ("GET", "/api/v1/workspaces/{workspace_id}"),
    ("POST", "/api/v1/workspaces"),
    ("PATCH", "/api/v1/workspaces/{workspace_id}"),
    ("DELETE", "/api/v1/workspaces/{workspace_id}"),
    ("GET", "/api/v1/workspaces/{workspace_id}/members"),
    ("POST", "/api/v1/workspaces/{workspace_id}/members"),
    ("PATCH", "/api/v1/workspaces/{workspace_id}/members/{user_id}"),
    ("DELETE", "/api/v1/workspaces/{workspace_id}/members/{user_id}"),
    ("GET", "/api/v1/workspaces/{workspace_id}/invitations"),
    ("POST", "/api/v1/workspaces/{workspace_id}/invitations"),
    ("DELETE", "/api/v1/workspaces/{workspace_id}/invitations/{invitation_id}"),
    ("GET", "/api/v1/workspaces/{workspace_id}/stats"),
    # tasks
    ("GET", "/api/v1/tasks"),
    ("GET", "/api/v1/tasks/identifier/{identifier}"),
    ("GET", "/api/v1/tasks/{task_id}"),
    ("POST", "/api/v1/tasks"),
    ("PATCH", "/api/v1/tasks/{task_id}"),
    ("DELETE", "/api/v1/tasks/{task_id}"),
    ("POST", "/api/v1/tasks/{task_id}/archive"),
    ("POST", "/api/v1/tasks/{task_id}/unarchive"),
    ("POST", "/api/v1/tasks/bulk/status"),
    # initiatives
    ("GET", "/api/v1/initiatives"),
    ("GET", "/api/v1/initiatives/{initiative_id}"),
    ("POST", "/api/v1/initiatives"),
    ("PATCH", "/api/v1/initiatives/{initiative_id}"),
    ("DELETE", "/api/v1/initiatives/{initiative_id}"),
    # projects
    ("GET", "/api/v1/projects"),
    ("GET", "/api/v1/projects/{project_id}"),
    ("POST", "/api/v1/projects"),
    ("PATCH", "/api/v1/projects/{project_id}"),
    ("DELETE", "/api/v1/projects/{project_id}"),
    # teams
    ("GET", "/api/v1/teams"),
    ("GET", "/api/v1/teams/{team_id}"),
    ("POST", "/api/v1/teams"),
    ("PATCH", "/api/v1/teams/{team_id}"),
    ("DELETE", "/api/v1/teams/{team_id}"),
    ("GET", "/api/v1/teams/{team_id}/members"),
    ("POST", "/api/v1/teams/{team_id}/members"),
    ("PATCH", "/api/v1/teams/{team_id}/members/{user_id}"),
    ("DELETE", "/api/v1/teams/{team_id}/members/{user_id}"),
    # comments
    ("GET", "/api/v1/comments"),
    ("GET", "/api/v1/comments/{comment_id}"),
    ("POST", "/api/v1/comments"),
    ("PATCH", "/api/v1/comments/{comment_id}"),
    ("DELETE", "/api/v1/comments/{comment_id}"),
    # attachments
    ("GET", "/api/v1/attachments"),
    ("GET", "/api/v1/attachments/{attachment_id}"),
    ("POST", "/api/v1/attachments"),
    ("PATCH", "/api/v1/attachments/{attachment_id}"),
    ("DELETE", "/api/v1/attachments/{attachment_id}"),
    # updates
    ("GET", "/api/v1/updates"),
    ("GET", "/api/v1/updates/{update_id}"),
    ("POST", "/api/v1/updates"),
    ("PATCH", "/api/v1/updates/{update_id}"),
    ("DELETE", "/api/v1/updates/{update_id}"),
}


def test_root_returns_message():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Gazior Ops server is running"}


def test_docs_and_openapi_ui_available():
    client = TestClient(app)
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200


def test_openapi_lists_all_v1_routes():
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    paths = spec.get("paths", {})
    registered = set()
    for path, methods in paths.items():
        for method in methods:
            if method.startswith("x-"):
                continue
            registered.add((method.upper(), path))

    missing = EXPECTED_ROUTE_METHODS - registered
    assert not missing, f"OpenAPI missing routes: {sorted(missing)}"
