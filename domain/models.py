from abc import ABC, abstractmethod
from domain.checks import Check
from domain.entities import CheckResult
from domain.exceptions import ModelExecutionError

class FinancialModelExecutor(ABC):

    @abstractmethod
    def _run(self, params: dict) -> dict: 
        pass

    def run(self, params: dict) -> dict:
        try:
            return self._run(params)
        
        except Exception as e:
            raise ModelExecutionError(f"Error during model execution: {e}.") from e

    @abstractmethod
    def _specific_checks(self) -> list[Check]:
        pass

    def __generic_checks(self) -> list[Check]:
        from domain.checks import OutputNotEmptyCheck
        return [
            OutputNotEmptyCheck()
        ]
    
    def run_checks(self, outputs: dict) -> list[CheckResult]:
        all_checks = self.__generic_checks() + self._specific_checks()
        return [
            check.run(outputs) for check in all_checks
        ]

    ### When defining checks, some should be generic (e.g. JSON need to be serializable!)
    ### other checks should (may!!!) be implemented by the specific models.
    ### ---> write docstrings
