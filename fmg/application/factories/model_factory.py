from fmg.domain.financial_model_executor import FinancialModelExecutor
from fmg.domain.financial_models.PortfolioValueAtRisk import PortfolioVaR

MODEL_REGISTRY = {
    (1, 1): PortfolioVaR,
}


class ModelFactory:
    ### to be Github-based!!!
    @staticmethod
    def get(model_id: int, version_id: int) -> FinancialModelExecutor:
        cls = MODEL_REGISTRY[(model_id, version_id)]
        return cls()
