import dataclasses
from enum import Enum
from typing import Any

from django.db import IntegrityError, OperationalError, ProgrammingError
from typing_extensions import override

from fmg.application.exceptions import (
    EarlyRunIdAssignmentError,
    MissingRunIdError,
    RunNotFoundError,
)
from fmg.application.interfaces.repositories_interfaces import IRunRepository
from fmg.domain.entities import ModelRun, RunStatus
from fmg.infra.django.models import ModelRunORM
from fmg.infra.exceptions import DatabaseError

# Follow up(s):
#   - which field should be updated (save) is not an infrastructural decision!
#


class DjangoRunRepository(IRunRepository):
    # ------------------------------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------------------------------

    @override
    def get(self, run_id: int) -> ModelRun:
        """
        Fetch an existing model run by its ID.

        Args:
            run_id: A unique identifier of a model run.

        Returns:
            The ModelRun instance associated with the given ID.

        Raises:
            RunNotFoundError: If the model run is not found.
            OperationalError: If a database error is encountered while fetching the model run.
        """
        try:
            orm_obj = ModelRunORM.objects.get(pk=run_id)
            return self._to_entity(orm_obj)

        except ModelRunORM.DoesNotExist as e:
            # Run does not exist (--> application-level error)
            raise RunNotFoundError(f"Run {run_id} not found.") from e

        except OperationalError as e:
            # Infrastructure-level error
            raise DatabaseError(f"Database error while fetching run {run_id}: {e}") from e

        except ProgrammingError as e:
            # SQL error
            raise DatabaseError(f"SQL error while fetching run {run_id}: {e}") from e

        # let other exceptions propagate: they are likely programming errors that should be fixed in the code, not handled at runtime.

    @override
    def create(self, run: ModelRun) -> int:
        """
        Persist a new run via INSERT.

        Args:
            run: The ModelRun instance of a model run.

        Returns:
            The ID associated with the persisted new run.

        Raises:
            EarlyRunIdAssignmentError: If the ModelRun already has an ID.
            DatabaseError: If the persistence layer fails due to integrity constraints or connectivity issues.
            InfrastructureError: If an unexpected infrastructural internal error occurs.
        """
        if run.run_id is not None:
            raise EarlyRunIdAssignmentError(
                f"Cannot create a new run from an instance that already has an ID: {run.run_id}. "
            )

        try:
            orm_obj = self._to_orm_for_insert(run)
            orm_obj.save()

            if not orm_obj.pk:
                raise DatabaseError("Database failed to return a primary key (run_id).")

            return orm_obj.pk

        except IntegrityError as e:
            # DB constraint violation
            raise DatabaseError(f"Integrity error while creating run: {e}") from e

        except OperationalError as e:
            # Infrastructure-level error
            raise DatabaseError(f"Database error while creating run: {e}") from e

    @override
    def save(self, run: ModelRun) -> None:
        """
        Persist an updated version of an existing model run via UPDATE.

        Args:
            run: The ModelRun instance of a model run.

        Raises:
            MissingRunIdError: If the ModelRun does not have a run_id.
            DatabaseError: If the persistence layer fails due to integrity constraints or connectivity issues.
            RunNotFoundError: If the model run was not found within the database.
        """
        if run.run_id is None:
            raise MissingRunIdError("Cannot update a run without a run_id.")

        # Mutable fields of a ModelRun
        raw_mutable_data = run.get_mutable_fields()
        updates = {k: self._serialize_for_db(v) for k, v in raw_mutable_data.items()}

        try:
            updated = ModelRunORM.objects.filter(pk=run.run_id).update(**updates)

        except OperationalError as e:
            raise DatabaseError(f"Database error while saving run {run.run_id}: {e}") from e

        if updated == 0:
            # No run was found in DB.
            raise RunNotFoundError(f"Run {run.run_id} not found during conditional update.")

    @override
    def save_if_status(self, run: ModelRun, expected_status: RunStatus) -> bool:
        """
        Persist the run if its current status matches expected_status.

        Atomically persists the run when the condition is met, protecting against race conditions.

        Args:
            run: The ModelRun instance of a model run.
            expected_status: The expected status of run.

        Returns:
            True if the update was persisted, False if the status had already changed.

        Raises:

        """
        if run.run_id is None:
            raise MissingRunIdError("Cannot update a run without a run_id.")

        ### ----> INCAPSULATE COMMON PART BETWEEN save and save_if_status ???

        # Mutable fields of a ModelRun
        raw_mutable_data = run.get_mutable_fields()
        updates = {k: self._serialize_for_db(v) for k, v in raw_mutable_data.items()}

        try:
            updated = ModelRunORM.objects.filter(
                pk=run.run_id,
                status=expected_status,
            ).update(**updates)

        except OperationalError as e:
            raise DatabaseError(
                f"Database error during conditional update of run {run.run_id}: {e}"
            ) from e

        if updated == 1:
            return True

        # Disambiguate reason behind updated == 0
        exists = ModelRunORM.objects.filter(pk=run.run_id).exists()
        if not exists:
            raise RunNotFoundError(f"Run {run.run_id} not found during conditional update.")

        # Run exists but status had already changes - race condition, expected
        return False

    # ------------------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------------------

    def _to_entity(self, orm_obj: ModelRunORM) -> ModelRun:
        """Map a Django ModelRunORM to a ModelRun domain entity."""
        from datetime import datetime

        from fmg.domain.entities import CheckResult
        from fmg.domain.enums import CheckOutcome, CheckSeverity, CheckType

        check_results = None
        if orm_obj.check_results is not None:
            check_results = [
                CheckResult(
                    check_name=cr["check_name"],
                    outcome=CheckOutcome(cr["outcome"]),
                    check_type=CheckType(cr["check_type"]),
                    check_severity=CheckSeverity(cr["check_severity"]),
                    message=cr["message"],
                    details=cr["details"],
                    started_at=datetime.fromisoformat(cr["started_at"]),
                    completed_at=datetime.fromisoformat(cr["completed_at"]),
                )
                for cr in orm_obj.check_results
            ]

        return ModelRun(
            run_id=orm_obj.pk,
            model_id=orm_obj.model_id,
            model_version_id=orm_obj.model_version_id,
            parameter_version_id=orm_obj.parameter_version_id,
            status=RunStatus(orm_obj.status),
            created_at=orm_obj.created_at,
            completed_at=orm_obj.completed_at,
            outputs=orm_obj.outputs,
            check_results=check_results,
            error_message=orm_obj.error_message,
        )  ### --> check dates implementation soundness!!!

    def _to_orm_for_insert(self, run: ModelRun) -> ModelRunORM:
        """Map a ModelRun domain entity to a Django ModelRunORM for INSERT."""
        return ModelRunORM(
            model_id=run.model_id,
            model_version_id=run.model_version_id,
            parameter_version_id=run.parameter_version_id,
            status=run.status.value,
            # created_at=run.created_at # this field has a default value in the ORM model, so we don't need to set it explicitly
            # --> do we need to include mutable fields as = None ???
        )

    def _serialize_for_db(self, field_data: Any) -> Any:
        """Helper for making domain field data JSON-friendly."""
        if isinstance(field_data, Enum):
            return field_data.value
        if dataclasses.is_dataclass(field_data) and not isinstance(field_data, type):
            return dataclasses.asdict(field_data)
        if isinstance(field_data, list):
            return [self._serialize_for_db(item) for item in field_data]
        if isinstance(field_data, dict):
            return {k: self._serialize_for_db(v) for k, v in field_data.items()}
        return field_data
