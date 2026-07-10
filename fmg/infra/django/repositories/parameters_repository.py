import dataclasses
from enum import Enum
from typing import Any

from fmg.application.exceptions import EarlyParamsSetIdAssignmentError, MissingParamsSetIdError, ParametersNotFoundError
from fmg.application.interfaces.repositories_interfaces import IParametersRepository

from django.db import OperationalError, IntegrityError, ProgrammingError

from fmg.domain.entities import ParameterSet
from fmg.infra.django.models import ParameterVersionORM
from fmg.infra.exceptions import DatabaseError


class DjangoParametersRepository(IParametersRepository):

    def get(self, parameter_set_id: int) -> ParameterSet:
        """
        Fetch an existing parameter set by its ID and associated model ID.
        
        Args:
            parameter_set_id: A unique identifier of a parameter set.
            
        Returns:
            The ParameterSet instance associated with the given ID.
        """
        try:
            orm_obj = ParameterVersionORM.objects.get(pk=parameter_set_id)
            return self._to_entity(orm_obj)
        
        except ParameterVersionORM.DoesNotExist:
            raise ParametersNotFoundError(
                f"Parameter set {parameter_set_id} not found."
            )
        
        except OperationalError as e:
            raise DatabaseError(
                f"Database error while fetching parameter set {parameter_set_id}: {e}"
            ) from e
        
        except ProgrammingError as e:
            raise DatabaseError(
                f"SQL error while fetching parameter set {parameter_set_id}: {e}"
            ) from e
        
        # let other exceptions propagate: they are likely programming errors that should be fixed in the code, not handled at runtime.


    def save(self, parameter_set: ParameterSet) -> None:
        """
        Persist an updated version of an existing parameter set via UPDATE.
        """
        if parameter_set.parameter_version_id is None:
            raise MissingParamsSetIdError(
                "Cannot save a parameter set that does not have an ID."
            )
        
        # Mutable fields of a ParameterSet
        raw_mutable_data = parameter_set.get_mutable_fields()
        updates = {
            k: self._serialize_for_db(v) for k, v in raw_mutable_data.items()
        }

        try:
            updated = ParameterVersionORM.objects.filter(
                pk=parameter_set.parameter_version_id
            ).update(
                **updates
            )
        
        except OperationalError as e:
            raise DatabaseError(
                f"Database error while saving parameter set {parameter_set.parameter_version_id}: {e}"
            ) from e
        
        if updated == 0:
            raise ParametersNotFoundError(
                f"Parameter set {parameter_set.parameter_version_id} not found during conditional update."
            )
        

    def save_if_status(self, parameter_set: ParameterSet, expected_status: bool) -> bool:
        """
        Atomically update an existing parameter set if its approved status matches the expected status.

        Args:
            parameter_set: The ParameterSet instance to be updated.
            expected_status: The expected approved status of the parameter set for the update to proceed.

        Returns:
            True if the update was successful, False otherwise.
        """
        if parameter_set.parameter_version_id is None:
            raise MissingParamsSetIdError(
                "Cannot save a parameter set that does not have an ID."
            )
        
        # Mutable fields of a ParameterSet
        raw_mutable_data = parameter_set.get_mutable_fields()
        updates = {
            k: self._serialize_for_db(v) for k, v in raw_mutable_data.items()
        }

        try:
            updated = ParameterVersionORM.objects.filter(
                pk=parameter_set.parameter_version_id,
                approved=expected_status
            ).update(
                **updates
            )
        
        except OperationalError as e:
            raise DatabaseError(
                f"Database error while saving parameter set {parameter_set.parameter_version_id}: {e}"
            ) from e
        
        if updated == 1:
            return True
        
        # Disambiguate reason behind updated == 0
        exists = ParameterVersionORM.objects.filter(pk=parameter_set.parameter_version_id).exists()
        if not exists:
            raise ParametersNotFoundError(
                f"Parameter set {parameter_set.parameter_version_id} not found during conditional update."
            )
        
        # Parameter set exists but status had already changed - race condition, expected
        return False

    
    def create(self, parameter_set: ParameterSet) -> int:
        """
        Persist a new parameter set via INSERT.
        """
        if parameter_set.parameter_version_id is not None:
            raise EarlyParamsSetIdAssignmentError(
                f"Cannot create a new parameter set from an instance that already has an ID: {parameter_set.parameter_version_id}. "
            )
        
        try:
            orm_obj = self._to_orm_for_insert(parameter_set)
            orm_obj.save()

            if not orm_obj.pk:
                raise DatabaseError(
                    "Database failed to return a primary key (parameter_version_id)."
                )
            
            return orm_obj.pk
        
        except IntegrityError as e:
            # DB constraint violation
            raise DatabaseError(
                f"Integrity error while creating parameter set: {e}"
            ) from e
        
        except OperationalError as e:
            # Infrastructure-level error
            raise DatabaseError(
                f"Database error while creating parameter set: {e}"
            ) from e
        

    
    # ------------------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------------------

    def _to_entity(self, orm_obj: ParameterVersionORM) -> ParameterSet:
        """
        Convert a Django ORM object to a domain entity.
        """
        return ParameterSet(
            parameter_version_id=orm_obj.pk,
            model_id=orm_obj.model_id,
            parameter_version=orm_obj.parameter_version,
            parameter_set=orm_obj.parameter_set,
            approved=orm_obj.approved,
            created_at=orm_obj.created_at
        )
    
    def _to_orm_for_insert(self, parameter_set: ParameterSet) -> ParameterVersionORM:
        """
        Convert a domain entity to a Django ORM object for insertion.
        """
        return ParameterVersionORM(
            model_id=parameter_set.model_id,
            parameter_version=parameter_set.parameter_version,
            parameter_set=parameter_set.parameter_set,
            # approved=parameter_set.approved # this field defaults to false in the ORM model
        )
    
    def _serialize_for_db(self, field_data: Any) -> Any:
        """Helper for making domain field data JSON-friendly."""
        if isinstance(field_data, Enum):
            return field_data.value
        if dataclasses.is_dataclass(field_data):
            return dataclasses.asdict(field_data)
        if isinstance(field_data, list):
            return [self._serialize_for_db(item) for item in field_data]
        if isinstance(field_data, dict):
            return {k: self._serialize_for_db(v) for k, v in field_data.items()}
        return field_data