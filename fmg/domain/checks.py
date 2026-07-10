from abc import ABC, abstractmethod
from fmg.domain.enums import CheckOutcome, CheckSeverity, CheckType
from fmg.domain.entities import CheckResult
from datetime import datetime, timezone

class Check(ABC):

    check_type: CheckType
    severity: CheckSeverity

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _execute(self, outputs: dict) -> tuple[CheckOutcome, str, dict]:
        pass

    
    def run(self, outputs: dict) -> CheckResult:
        
        start_time = datetime.now(timezone.utc)
        outcome, message, details = self._execute(outputs)
        completion_time = datetime.now(timezone.utc)

        return CheckResult(
            self.name,
            outcome,
            self.check_type,
            self.severity,
            message,
            details,
            start_time,
            completion_time
        )
    

class OutputNotEmptyCheck(Check):

    check_type = CheckType.GENERIC
    severity = CheckSeverity.ERROR

    @property
    def name(self) -> str:
        return "output_not_empty"
    
    def _execute(self, outputs: dict) -> tuple[CheckOutcome, str, dict]:
        
        if outputs and len(outputs) > 0:
            return (
                CheckOutcome.PASSED, 
                "Output is non-empty.", 
                {}
            )
        else:
            return (
                CheckOutcome.FAILED,
                "Output is empty.",
                {}
            )
