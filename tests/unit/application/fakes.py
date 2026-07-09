from datetime import datetime, timezone

from application.factories.model_factory import ModelFactory
from application.interfaces.repositories_interfaces import IParametersRepository, IRunRepository
from domain.entities import ModelRun, ParameterSet
from domain.financial_model_executor import FinancialModelExecutor

mock_parameters = ParameterSet(
    parameter_version_id=None,
    model_id=0,
    parameter_version="fake_version",
    parameter_set={"this_is": "a_fake_parameter_set"},
    approved=False,
    created_at=datetime.now(timezone.utc),
)

class FakeModel(FinancialModelExecutor):
    def _run(self, params: dict) -> dict:
        return {"var_95": 0.023}

class FakeModelFactory(ModelFactory):
    @staticmethod
    def get(model_id: int, version_id: int) -> FinancialModelExecutor:
        return FakeModel()

class FakeParametersRepository(IParametersRepository):
    def get(self, parameter_set_id: int) -> ParameterSet:
        return mock_parameters
    
    def create(self, parameter_set):
        return super().create(parameter_set)
    
    def save(self, parameter_set):
        return super().save(parameter_set)

class InMemoryRunRepository(IRunRepository):
    def __init__(self, run: ModelRun):
        self._run = run
        self.save_calls = 0

    def get(self, run_id: int) -> ModelRun:
        return self._run

    def save(self, run: ModelRun):
        self._run = run
        self.save_calls += 1

    def save_if_status(self, run, expected_status):
        return super().save_if_status(run, expected_status)
    
    def create(self, run: ModelRun) -> int:
        return super().create(run)

class FakeTaskDispatcher:
    def __init__(self):
        self.dispatched: list[int] = []

    def dispatch_checks(self, run_id: int):
        self.dispatched.append(run_id)