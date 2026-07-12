import pytest
from celery.contrib.testing.worker import start_worker
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(scope="module")
def celery_worker():
    from fmg.infra.celery.app import app

    with start_worker(app, perform_ping_check=False, pool="solo") as worker:
        yield worker
