# tests/unit/application/test_run_model_service.py
from datetime import datetime, timezone

import pytest
from fmg.application.factories.model_factory import ModelFactory
from fmg.application.services.run_model_service import RunModelService
from fmg.domain.entities import ModelRun
from fmg.domain.enums import RunStatus
from .fakes import (
    FakeModelFactory, FakeParametersRepository,
    InMemoryRunRepository, FakeTaskDispatcher,
)

def make_run(status: RunStatus = RunStatus.PENDING) -> ModelRun:
    return ModelRun(
        run_id=1,
        model_id=0,
        model_version_id=0,
        parameter_version_id=0,
        status=status,
        created_at=datetime.now(timezone.utc),
    )

def test_success_dispatches_checks():
    run = make_run(RunStatus.PENDING)
    run_repo = InMemoryRunRepository(run)
    dispatcher = FakeTaskDispatcher()

    service = RunModelService(
        run_repository=run_repo,
        parameters_repository=FakeParametersRepository(),
        model_factory=FakeModelFactory(),
        task_dispatcher=dispatcher,
    )
    service.run_model(run.run_id)

    assert run_repo._run.status == RunStatus.OUTPUTS_GENERATED
    assert dispatcher.dispatched == [run.run_id]

def test_model_factory_failure_marks_run_as_failed():
    run = make_run(RunStatus.PENDING)
    run_repo = InMemoryRunRepository(run)
    dispatcher = FakeTaskDispatcher()

    class BoomModelFactory(ModelFactory):
        def get(self, model_id, model_version_id):
            raise ValueError("model not found")

    service = RunModelService(
        run_repository=run_repo,
        parameters_repository=FakeParametersRepository(),
        model_factory=BoomModelFactory(),
        task_dispatcher=dispatcher,
    )
    service.run_model(run.run_id)

    assert run_repo._run.status == RunStatus.FAILED
    assert dispatcher.dispatched == []  # no checks should be triggered on a failed run

def test_non_pending_run_is_skipped():
    run = make_run(RunStatus.RUNNING)  # già in corso, concorrenza
    run_repo = InMemoryRunRepository(run)
    dispatcher = FakeTaskDispatcher()

    service = RunModelService(
        run_repository=run_repo,
        parameters_repository=FakeParametersRepository(),
        model_factory=FakeModelFactory(),
        task_dispatcher=dispatcher,
    )
    service.run_model(run.run_id)

    assert run_repo.save_calls == 0  # nessun side-effect, early return rispettato