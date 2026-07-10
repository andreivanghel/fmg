from fmg.application.factories.model_factory import ModelFactory
from fmg.domain.financial_model_executor import FinancialModelExecutor


class FakeModel(FinancialModelExecutor):
    def _run(self, params: dict) -> dict:
        return {"var_95": 0.023, "var_99": 0.041}  # >1 chiave, serve a passare OutputNotEmptyCheck


class FakeModelFactory(ModelFactory):
    @staticmethod
    def get(model_id: int, version_id: int) -> FinancialModelExecutor:
        return FakeModel()