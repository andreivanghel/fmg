from domain.models import FinancialModel
from domain.financial_models.PortfolioValueAtRisk import PortfolioVaR

class ModelFactory:

    ### to be Github-based!!!
    @staticmethod
    def get(model_id: str, model_version: str) -> FinancialModel:

        if model_id == "1" and model_version == "1":
            return PortfolioVaR()
        else:
            raise FileNotFoundError(f"Il modello {model_id} con versione {model_version} non è stato trovato.")