import time
import pytest
from domain.enums import RunStatus
from tests.common.fakes import FakeModelFactory
from tests.smoke.factories import (
    FinancialModelORMFactory, ModelVersionORMFactory, ParameterVersionORMFactory,
)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_run_checks_end_to_end_real_broker(api_client, celery_worker, monkeypatch):
    monkeypatch.setattr("infra.celery.tasks.ModelFactory", FakeModelFactory)

    model = FinancialModelORMFactory()
    model_version = ModelVersionORMFactory(model=model)
    param = ParameterVersionORMFactory(model=model)

    response = api_client.post(
        "/api/v1/runs/",
        data={
            "model_id": model.pk,
            "model_version_id": model_version.pk,
            "parameter_version_id": param.pk,
        },
        format="json",
    )
    assert response.status_code == 202
    run_id = response.data["run_id"]

    from infra.django.models import ModelRunORM
    for _ in range(20):
        run = ModelRunORM.objects.get(run_id=run_id)
        if run.status == RunStatus.COMPLETED.value:
            break
        time.sleep(0.5)
    else:
        pytest.fail("il task non ha completato entro il timeout: possibile problema di broker/serializzazione")

    assert run.status == RunStatus.COMPLETED.value