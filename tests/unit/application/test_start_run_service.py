from fmg.application.services.start_run_service import StartRunService
from fmg.domain.enums import RunStatus

from .fakes import FakeTaskDispatcher, InMemoryRunRepository


def test_start_run_creates_and_dispatches():
    run_repo = InMemoryRunRepository()
    dispatcher = FakeTaskDispatcher()

    service = StartRunService(run_repository=run_repo, task_dispatcher=dispatcher)

    run_id = service.start_run(model_id=1, model_version_id=2, parameter_version_id=3)

    assert run_id == 1
    assert run_repo._run is not None
    assert run_repo._run.model_id == 1
    assert run_repo._run.model_version_id == 2
    assert run_repo._run.parameter_version_id == 3
    assert run_repo._run.status == RunStatus.PENDING
    assert dispatcher.dispatched_runs == [run_id]
