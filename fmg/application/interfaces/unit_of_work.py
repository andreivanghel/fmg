from abc import ABC, abstractmethod

# TODO: this is a duplicate of the IUnitOfWork interface in fmg/application/interfaces/unit_of_work.py.
# We should remove one of them and use the other consistently across the codebase.


class IUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
