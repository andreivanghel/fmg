import pytest
from rest_framework.test import APIClient
from celery.contrib.testing.worker import start_worker


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(scope="module")
def celery_worker():
    from infra.celery.app import app
    with start_worker(app, perform_ping_check=False, pool="solo") as worker:
        yield worker