import time

import pytest

from fmg.domain.enums import RunStatus
from tests.common.fakes import FakeModelFactory
from tests.smoke.factories import (
    FinancialModelORMFactory,
    ModelVersionORMFactory,
    ParameterVersionORMFactory,
)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
def test_run_checks_end_to_end_real_broker(api_client, celery_worker, monkeypatch):
    monkeypatch.setattr("fmg.infra.celery.tasks.ModelFactory", FakeModelFactory)

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

    from fmg.infra.django.models import ModelRunORM

    for _ in range(20):
        run = ModelRunORM.objects.get(run_id=run_id)
        if run.status in (RunStatus.COMPLETED.value, RunStatus.FAILED.value):
            break
        time.sleep(0.5)
    else:
        pytest.fail(
            "il task non ha raggiunto uno stato finale entro il timeout — problema di broker/dispatch"
        )

    assert run.status == RunStatus.COMPLETED.value, (
        f"Run terminato con status={run.status}, error_message={run.error_message!r}"
    )
