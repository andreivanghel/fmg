from django.db import transaction
from application.interfaces.unit_of_work import IUnitOfWork


class DjangoUnitOfWork(IUnitOfWork):

    def __enter__(self):
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        return self._atomic.__exit__(exc_type, exc_val, exc_tb)

    def commit(self) -> None:
        pass  # Django commits if no exception is raised within the block

    def rollback(self) -> None:
        transaction.set_rollback(True)