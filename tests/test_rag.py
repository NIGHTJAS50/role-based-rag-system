from fastapi.testclient import TestClient
from app.main import app

def test_role_filter_blocks_guest():
    response = TestClient(app).post('/query', json={'question': 'deploy'}, headers={'X-Role': 'guest'})
    assert response.status_code == 403

def test_engineering_context_is_retrieved():
    response = TestClient(app).post('/query', json={'question': 'deploy pipeline'}, headers={'X-Role': 'engineering'})
    assert response.status_code == 200
    assert 'CI pipeline' in response.json()['answer']
