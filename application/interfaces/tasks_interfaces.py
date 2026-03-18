from abc import ABC, abstractmethod

class ITaskDispatcher(ABC):

    @abstractmethod
    def dispatch_run(self, run_id: str) -> None:
        pass

    @abstractmethod
    def dispatch_checks(self, run_id: str) -> None:
        pass