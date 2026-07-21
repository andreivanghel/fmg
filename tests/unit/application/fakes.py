from datetime import UTC, datetime

from typing_extensions import override

from fmg.application.factories.model_factory import ModelFactory
from fmg.application.interfaces.repositories_interfaces import IParametersRepository, IRunRepository
from fmg.application.interfaces.tasks_interfaces import ITaskDispatcher
from fmg.domain.entities import ModelRun, ParameterSet
from fmg.domain.enums import RunStatus
from fmg.domain.financial_model_executor import FinancialModelExecutor

mock_parameters = ParameterSet(
    parameter_version_id=None,
    model_id=0,
    parameter_version="fake_version",
    parameter_set={"this_is": "a_fake_parameter_set"},
    approved=False,
    created_at=datetime.now(UTC),
)


class FakeModel(FinancialModelExecutor):
    @override
    def _run(self, params: dict) -> dict:
        return {"var_95": 0.023}


class FakeModelFactory(ModelFactory):
    @override
    @staticmethod
    def get(model_id: int, version_id: int) -> FinancialModelExecutor:
        return FakeModel()


class FakeParametersRepository(IParametersRepository):
    def __init__(self):
        self._next_id = 1
        self._status = False

    @override
    def get(self, parameter_set_id: int) -> ParameterSet:
        return mock_parameters

    @override
    def create(self, parameter_set: ParameterSet) -> int:
        generated_id = self._next_id
        self._next_id += 1
        return generated_id

    @override
    def save(self, parameter_set: ParameterSet) -> None:
        pass  # maybe make it store the parameter_set in memory for testing purposes (only if needed in tests)

    @override
    def save_if_status(self, parameter_set: ParameterSet, expected_status: bool) -> bool:
        if self._status == expected_status:
            self.save(parameter_set)
            return True
        else:
            return False


class InMemoryRunRepository(IRunRepository):
    def __init__(self, run: ModelRun | None = None):
        self._run = run
        self.save_calls = 0
        self._next_id = 1

    @override
    def get(self, run_id: int) -> ModelRun:
        assert self._run is not None, "InMemoryRunRepository: no run stored in memory"
        return self._run

    @override
    def save(self, run: ModelRun):
        self._run = run
        self.save_calls += 1

    @override
    def save_if_status(self, run: ModelRun, expected_status: RunStatus) -> bool:
        if self._run is None or self._run.status != expected_status:
            return False
        self._run = run
        self.save_calls += 1
        return True

    @override
    def create(self, run: ModelRun) -> int:
        generated_id = self._next_id
        self._next_id += 1
        self._run = run
        return generated_id


class FakeTaskDispatcher(ITaskDispatcher):
    def __init__(self):
        self.dispatched_runs: list[int] = []
        self.dispatched_checks: list[int] = []

    @override
    def dispatch_run(self, run_id: int) -> None:
        self.dispatched_runs.append(run_id)

    @override
    def dispatch_checks(self, run_id: int) -> None:
        self.dispatched_checks.append(run_id)
