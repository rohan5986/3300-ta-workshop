from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

VALID_PRIORITIES = {"Low", "Medium", "High"}
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report", "priority": "Medium"},
    {"id": 2, "title": "Project-2 MMFs", "priority": "Medium"}
]
next_id = 3


def normalize_task(task):
    """Ensure a task has a valid priority value."""
    if task.get("priority") not in VALID_PRIORITIES:
        task["priority"] = DEFAULT_PRIORITY
    return task


@app.route('/')
def index():
    """Render the task tracker page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks with their priorities."""
    return jsonify([normalize_task(task) for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a task with a title and optional priority."""
    global next_id
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    priority = data.get("priority") or DEFAULT_PRIORITY
    if priority not in VALID_PRIORITIES:
        return jsonify({
            "error": "Priority must be Low, Medium, or High"
        }), 400

    new_task = {
        "id": next_id,
        "title": data['title'],
        "priority": priority
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task by its ID."""
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return jsonify({"result": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
