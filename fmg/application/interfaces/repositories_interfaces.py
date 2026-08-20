from abc import ABC, abstractmethod

from fmg.domain.entities import ModelRun, ParameterSet, RunStatus


class IModelRepository(ABC):
    """Interface for FinancialModel repositories (model metadata, e.g. VaR model).
    TODO: concrete implementation and dedicated model factory not yet done —
    CreateParametersSetService that uses it is not in the scope of the current MVP
    (parameters are inserted manually via ORM for now).
    """

    @abstractmethod
    def get_all_models_ids(self) -> list[int]:
        pass


class IRunRepository(ABC):
    @abstractmethod
    def get(self, run_id: int) -> ModelRun:
        pass

    @abstractmethod
    def create(self, run: ModelRun) -> int:
        """INSERT - returns the generated run_id"""
        pass

    @abstractmethod
    def save(self, run: ModelRun) -> None:
        """UPDATE - updates an existing run"""
        pass

    @abstractmethod
    def save_if_status(self, run: ModelRun, expected_status: RunStatus) -> bool:
        """Atomic UPDATE - updates an existing run is its expected status is expected_status.
        Returns True if the update is completed, and False otherwise"""
        pass


class IParametersRepository(ABC):
    @abstractmethod
    def create(self, parameter_set: ParameterSet) -> int:
        """INSERT - returns the generated parameters_id"""
        pass

    @abstractmethod
    def save(self, parameter_set: ParameterSet) -> None:
        pass

    @abstractmethod
    def save_if_status(self, parameter_set: ParameterSet, expected_status: bool) -> bool:
        pass

    @abstractmethod
    def get(self, parameter_set_id: int) -> ParameterSet:
        pass


class IUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class IOutboxRepository(ABC):
    @abstractmethod
    def save(self, event) -> None:
        pass

    @abstractmethod
    def get_pending(self, limit: int):
        pass

    @abstractmethod
    def mark_as_sent(self, event_id: str) -> None:
        pass


class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event) -> None:
        pass


class IAuditLogger(ABC):
    @abstractmethod
    def log_event(
        self, action: str, entity_type: str, entity_id: str, user: str, details: dict
    ) -> None:
        """
        Writes a log row in the audit log.
        """
        pass
