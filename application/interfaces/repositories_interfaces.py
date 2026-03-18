from domain.entities import ModelRun, ParameterSet
from abc import ABC, abstractmethod

class IRunRepository(ABC):
    
    @abstractmethod
    def save(self, run: ModelRun) -> None:
        pass

    @abstractmethod
    def get(self, run_id: str) -> ModelRun:
        pass

class IParametersRepository(ABC):

    @abstractmethod
    def save(self, parameter_set: ParameterSet) -> None:
        pass

    @abstractmethod
    def get(self, model_id: str, parameters_id: str) -> ParameterSet:
        pass
