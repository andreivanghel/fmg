from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from domain.enums import RunStatus, CheckType, CheckOutcome, CheckSeverity
from domain.exceptions import InvalidStateTransitionError

### --> manage what happens after a run is finished... 
###     for each method that performs some action on via RunRepository...!

@dataclass(frozen=True)
class ModelVersion:
    model_id: str
    version: str
    code_version: str
    approved: bool
    created_at: datetime

    @classmethod
    def create(
        cls, 
        model_id: str, 
        version: str, 
        code_version: str
    ):
        """
        Used to create a new model version.
        """
        return cls(
            model_id = model_id,
            version = version,
            code_version = code_version,
            approved = False,
            created_at = datetime.now(timezone.utc)
        )
    
    @classmethod
    def reconstitute(
        cls,
        model_id: str,
        version: str,
        code_version: str,
        approved: bool,
        created_at: datetime
    ):
        """
        Used by the repository to reconstitute from DB
        """
        return cls(
            model_id = model_id,
            version = version,
            code_version = code_version,
            approved = approved,
            created_at = created_at
        )
    

### this class cannot be frozen (unless reimplemented in some other form)
### when creating a new parameter version we don't know its number
### when writing to DB we only need (as inputs to the repository) model_id and parameters set (dict)
### we don't even need an instance of this class for this very simple task!!!
### ---> we can consider this class as a read-only object coming from the DB. <---
### this is definitely not a clean way to proceed though
@dataclass
class ParameterSet:
    model_id: str
    parameter_version: str | None
    parameter_set: dict
    approved: bool
    created_at: datetime


@dataclass(frozen=True)
class CheckResult:
    check_name: str
    outcome: CheckOutcome
    check_type: CheckType
    check_severity: CheckSeverity
    message: str
    details: dict
    started_at: datetime
    completed_at: datetime


@dataclass(frozen=True)
class ModelRun:
    id: str | None
    model_id: str
    model_version: str
    parameters_version: str
    status: RunStatus
    created_at: datetime
    completed_at: datetime | None = None
    outputs: dict[str, any] | None = None
    check_results: list[CheckResult] | None = None
    error_message: str | None = None

    @classmethod
    def create(
            cls, 
            model_id: str, 
            model_version: str,
            parameters_version: str
    ) -> ModelRun:
        return cls(
            id = None,
            model_id = model_id,
            model_version = model_version,
            parameters_version = parameters_version,
            status = RunStatus.PENDING,
            created_at = datetime.now(timezone.utc),
            completed_at = None,
            outputs = None,
            check_results = None,
            error_message = None
        )
    
    @classmethod
    def reconstitute(
        cls,
        **kwargs
    ) -> ModelRun:
        return cls(
            **kwargs
        )
    
    def apply_checks(self, check_results: list[CheckResult]) -> ModelRun:
        """
        Sets the check results and determines the final state of the run, returning a new instance of the class.
        """
        self.check_results = check_results

        has_critical_failures = any(
            c.outcome == CheckOutcome.FAILED and c.check_severity == CheckSeverity.ERROR
            for c in check_results
        )

        if has_critical_failures:
            self.mark_as_checks_failed(check_results)
        else:
            self.mark_as_completed(check_results)
    
    def mark_as_running(self) -> None:
        self.status = RunStatus.RUNNING

    def mark_as_outputs_generated(self, outputs: dict) -> None:
        self.status = RunStatus.OUTPUTS_GENERATED
        self.outputs = outputs
        
    def mark_as_completed(self, check_results: list[CheckResult]) -> None:
        allowed_states = [RunStatus.CHECKS_ERROR, RunStatus.OUTPUTS_GENERATED]
        if self.status not in allowed_states:
            raise InvalidStateTransitionError(
                f"Model run cannot transition from state {self.status} to state {RunStatus.COMPLETED}, "
                f"must be {allowed_states}."
            )
        
        self.status = RunStatus.COMPLETED
        self.check_results = check_results
        self.completed_at = datetime.now(timezone.utc)

    def mark_as_checks_failed(self, check_results: list[CheckResult]) -> None:
        self.status = RunStatus.CHECKS_FAILED
        self.check_results = check_results

    def mark_as_checks_error(self, error: str) -> None:
        self.status = RunStatus.CHECKS_ERROR
        self.error_message = error

    def mark_as_failed(self, error: str) -> None:
        self.status = RunStatus.FAILED
        self.error_message = error
    