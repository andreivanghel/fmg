import pytest

from fmg.domain.enums import RunStatus
from tests.common.fakes import FakeModelFactory

from .factories import FinancialModelORMFactory, ModelVersionORMFactory, ParameterVersionORMFactory


@pytest.mark.django_db
def test_run_checks_end_to_end(api_client, monkeypatch):
    monkeypatch.setattr(
        "fmg.infra.celery.tasks.ModelFactory", FakeModelFactory
    )  # Until we have a proper DI container, we need to monkeypatch the ModelFactory used in the Celery tasks to use our FakeModelFactory for testing.

    model = FinancialModelORMFactory()
    model_version = ModelVersionORMFactory(model=model)
    param = ParameterVersionORMFactory(model=model)

    response = api_client.post(
        "/api/v1/runs/",
        data={
            "model_id": model.pk,  # type: ignore[attr-defined]
            "model_version_id": model_version.pk,  # type: ignore[attr-defined]
            "parameter_version_id": param.pk,  # type: ignore[attr-defined]
        },
        format="json",
    )
    assert response.status_code == 202
    run_id = response.data["run_id"]

    info_response = api_client.get(f"/api/v1/runs/{run_id}/")
    assert info_response.status_code == 200
    assert info_response.data["status"] == RunStatus.COMPLETED.value
