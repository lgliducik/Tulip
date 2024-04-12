import pytest
from main import app as flask_app


@pytest.fixture()
def app():
    flask_app.testing = True
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_add_task(client, mongodb):
    response = client.post("/", data={"name": "task1"})
    print(list(mongodb.todo.find()))
    assert response.status_code == 200


def test_todo(mongodb):
    assert 'todo' in mongodb.list_collection_names()
    manuel = mongodb.todo.find_one({'task_name': 'task1'})
    assert manuel['status'] == 1
