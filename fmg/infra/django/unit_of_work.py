from django.db import transaction
from typing_extensions import override

from fmg.application.interfaces.unit_of_work import IUnitOfWork


class DjangoUnitOfWork(IUnitOfWork):
    @override
    def __enter__(self):
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
        return self

    @override
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        return self._atomic.__exit__(exc_type, exc_val, exc_tb)

    @override
    def commit(self) -> None:
        pass  # Django commits if no exception is raised within the block

    @override
    def rollback(self) -> None:
        transaction.set_rollback(True)
