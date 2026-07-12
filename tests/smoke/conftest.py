# tests/smoke/conftest.py
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def _celery_eager():
    from fmg.infra.celery.app import app

    original = app.conf.task_always_eager, app.conf.task_eager_propagates
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True
    yield
    app.conf.task_always_eager, app.conf.task_eager_propagates = original
