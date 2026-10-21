import pytest

import app as app_module
from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset tasks and task IDs before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])
    app_module.next_id = 3


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data
    assert b'id="task-priority"' in response.data
    assert b'value="Low"' in response.data
    assert b'value="Medium"' in response.data
    assert b'value="High"' in response.data


def test_get_tasks_defaults_missing_priority_to_medium(client):
    """Return Medium for older tasks without a priority."""
    response = client.get('/api/tasks')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


def test_add_task_success(client):
    """Create a task with the requested priority."""
    response = client.post(
        '/api/tasks',
        json={"title": "Test new task", "priority": "High"}
    )

    assert response.status_code == 201
    created_task = response.get_json()
    assert created_task['title'] == "Test new task"
    assert created_task['priority'] == "High"

    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3
    assert get_response.get_json()[-1]['priority'] == "High"


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_accepts_all_priorities(client, priority):
    """Accept each supported task priority."""
    response = client.post(
        '/api/tasks',
        json={"title": "Priority task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == priority


def test_add_task_defaults_priority_to_medium(client):
    """Default a newly created task to Medium when omitted."""
    response = client.post('/api/tasks', json={"title": "Default task"})

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_rejects_invalid_priority(client):
    """Reject priorities outside the supported values."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid task", "priority": "Urgent"}
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Priority must be Low, Medium, or High"
    }


def test_get_tasks_returns_stored_priorities(client):
    """Return stored priorities without changing valid values."""
    tasks[0]['priority'] = 'Low'
    tasks[1]['priority'] = 'High'

    response = client.get('/api/tasks')

    assert response.status_code == 200
    assert [task['priority'] for task in response.get_json()] == [
        'Low',
        'High'
    ]


def test_frontend_renders_priority(client):
    """Include priority data and priority classes in the frontend."""
    with open('static/app.js', encoding='utf-8') as app_file:
        app_source = app_file.read()

    assert 'task.priority' in app_source
    assert 'priority-${priorityClass}' in app_source
    assert 'Priority: ${priorityValue}' in app_source


def test_add_task_missing_title(client):
    """Reject task requests without a title."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()

    response = client.post('/api/tasks', json={})
    assert response.status_code == 400


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
