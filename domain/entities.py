from __future__ import annotations
from dataclasses import dataclass, replace, field, fields
from typing import Any
from datetime import datetime, timezone
from domain.enums import FieldMutability, RunStatus, CheckType, CheckOutcome, CheckSeverity
from domain.exceptions import InvalidStateTransitionError, EmptyParameterSet

# TODO: use the same exact naming everywhere within this project

### --> manage what happens after a run is finished... 
###     for each method that performs some action on via RunRepository...!
@dataclass(frozen=True)
class FinancialModel:
    model_id: int | None
    model_name: str
    description: str
    is_active: bool
    created_at: datetime
### write create / reconstitute...


@dataclass(frozen=True)
class ModelVersion:
    version_id: int | None
    model_id: int
    version: str
    code_version: str
    approved: bool
    created_at: datetime

    @classmethod
    def create(
        cls, 
        model_id: int, 
        version: str,
        code_version: str
    ) -> ModelVersion:
        """
        Used to create a new model version.
        """
        return cls(
            version_id = None,
            model_id = model_id,
            version = version,
            code_version = code_version,
            approved = False,
            created_at = datetime.now(timezone.utc)
        )
    
    @classmethod
    def reconstitute(
            cls,
            version_id: int,
            model_id: int,
            version: str,
            code_version: str,
            approved: bool,
            created_at: datetime
    ) -> ModelVersion:
        """
        Used by the repository to reconstitute from DB
        """
        return cls(
            version_id = version_id,
            model_id = model_id,
            version = version,
            code_version = code_version,
            approved = approved,
            created_at = created_at
        )
    
    def approve(self) -> ModelVersion:
        """
        Evolves the model version to approved state.
        """

        if self.approved:
            raise InvalidStateTransitionError(
                f"The model version {self.version} for model {self.model_id} is already approved."
            )
        
        return replace(
            self,
            approved = True
        )



@dataclass(frozen=True)
class ParameterSet:
    parameter_version_id: int | None
    model_id: int = field(metadata={"mutability": FieldMutability.IMMUTABLE})
    parameter_version: str = field(metadata={"mutability": FieldMutability.MUTABLE})
    parameter_set: dict = field(metadata={"mutability": FieldMutability.MUTABLE})
    approved: bool = field(metadata={"mutability": FieldMutability.CONTROLLED})
    created_at: datetime = field(metadata={"mutability": FieldMutability.IMMUTABLE})

    def get_mutable_fields(self) -> dict[str, Any]: # this is a little contamination of the domain entity with the repository implementation, but it is a convenient way to get the fields that can be updated during the life cycle of a model run.
        """
        Returns the field that be updated during the life cycle of a parameter set.
        """
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.metadata.get("mutability") == FieldMutability.MUTABLE
        }

    @classmethod
    def create(
            cls,
            model_id: int,
            parameter_version: str,
            parameter_set: dict
    ) -> ParameterSet:
        """
        Used to create a new parameter set.
        """
        if not parameter_set:
            raise EmptyParameterSet(
                "parameter_set cannot be empty."
            )
        
        return cls(
            parameter_version_id = None,
            model_id = model_id,
            parameter_version = parameter_version,
            parameter_set = parameter_set,
            approved = False,
            created_at = datetime.now(timezone.utc)
        )
    
    @classmethod
    def reconstitute(
            cls,
            parameter_version_id: int,
            model_id: int,
            parameter_version: str,
            parameter_set: dict,
            approved: bool,
            created_at: datetime
    ) -> ParameterSet:
        """
        Used by the repository to reconstitute from DB
        """
        return cls(
            parameter_version_id = parameter_version_id,
            model_id = model_id,
            parameter_version = parameter_version,
            parameter_set = parameter_set,
            approved = approved,
            created_at = created_at
        )

    def approve(self) -> ParameterSet:
        """
        Evolves the parameter set to approved state.
        """

        if self.approved:
            raise InvalidStateTransitionError(
                f"The parameter version {self.parameter_version} for model {self.model_id} is already approved."
            )

        return replace(
            self,
            approved = True
        )



@dataclass(frozen=True)
class CheckResult:
    check_name: str
    outcome: CheckOutcome
    check_type: CheckType
    check_severity: CheckSeverity
    message: str
    details: dict[str, Any]
    started_at: datetime
    completed_at: datetime



@dataclass(frozen=True)
class ModelRun:
    run_id: int | None
    model_id: int = field(metadata={"mutable": False})
    model_version_id: int = field(metadata={"mutable": False})
    parameter_version_id: int = field(metadata={"mutable": False})
    status: RunStatus = field(metadata={"mutable": True})
    created_at: datetime = field(metadata={"mutable": False})
    completed_at: datetime | None = field(default=None, metadata={"mutable": True})
    outputs: dict[str, Any] | None = field(default=None, metadata={"mutable": True})
    check_results: list[CheckResult] | None = field(default=None, metadata={"mutable": True})
    error_message: str | None = field(default=None, metadata={"mutable": True})

    def get_mutable_fields(self) -> dict[str, Any]: # this is a little contamination of the domain entity with the repository implementation, but it is a convenient way to get the fields that can be updated during the life cycle of a model run.
        """
        Returns the field that be updated during the life cycle of a model run.
        """
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.metadata.get("mutable", False)
        }

    @classmethod
    def create(
            cls, 
            model_id: int, 
            model_version_id: int,
            parameter_version_id: int
    ) -> ModelRun:
        return cls(
            run_id = None,
            model_id = model_id,
            model_version_id = model_version_id,
            parameter_version_id = parameter_version_id,
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
    
    def apply_checks(
            self, 
            check_results: list[CheckResult]
    ) -> ModelRun:
        """
        Sets the check results and determines the final state of the run, returning a new instance of the class.
        """

        has_critical_failures = any(
            c.outcome == CheckOutcome.FAILED and c.check_severity == CheckSeverity.ERROR
            for c in check_results
        )

        if has_critical_failures:
            next_status = RunStatus.CHECKS_FAILED
        else:
            next_status = RunStatus.COMPLETED

        allowed_states = [RunStatus.OUTPUTS_GENERATED]
        if self.status not in allowed_states:
            raise InvalidStateTransitionError(
                f"Model run cannot transition from state {self.status} to state {next_status}, "
                f"must be {allowed_states}."
            )

        return replace(
            self,
            check_results = check_results,
            status = next_status,
            completed_at = datetime.now(timezone.utc)
        )
    
    def apply_outputs(
            self, 
            outputs: dict[str, Any]
    ) -> ModelRun:
        
        next_state = RunStatus.OUTPUTS_GENERATED
        allowed_states = [RunStatus.RUNNING]

        if self.status not in allowed_states:
            raise InvalidStateTransitionError(
                f"Model run cannot transition from state {self.status} to state {next_state}, "
                f"must be {allowed_states}."
            )

        return replace(
            self,
            status = next_state,
            outputs = outputs
        )
    
    def mark_as_running(self) -> ModelRun:

        next_state = RunStatus.RUNNING
        allowed_states = [RunStatus.PENDING]

        if self.status not in allowed_states:
            raise InvalidStateTransitionError(
                f"Model run cannot transition from state {self.status} to state {next_state}, "
                f"must be {allowed_states}."
            )
        
        return replace(
            self,
            status = next_state
        )
        
    def mark_as_checks_error(
            self, 
            error: str
    ) -> ModelRun:

        next_state = RunStatus.CHECKS_ERROR
        allowed_states = [RunStatus.OUTPUTS_GENERATED]

        if self.status not in allowed_states:
            raise InvalidStateTransitionError(
                f"Model run cannot transition from state {self.status} to state {next_state}, "
                f"must be {allowed_states}."
            )
        
        return replace(
            self,
            status = RunStatus.CHECKS_ERROR,
            error_message = error,
            completed_at = datetime.now(timezone.utc)
        )

    def mark_as_failed(
            self, 
            error: str
    ) -> ModelRun:

        next_state = RunStatus.FAILED
        allowed_states = [RunStatus.RUNNING]

        if self.status not in allowed_states:
            raise InvalidStateTransitionError(
                f"Model run cannot transition from state {self.status} to state {next_state}, "
                f"must be {allowed_states}."
            )
        
        return replace(
            self,
            status = next_state,
            error_message = error,
            completed_at = datetime.now(timezone.utc)
        )
