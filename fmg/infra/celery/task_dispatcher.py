from typing_extensions import override

from fmg.application.interfaces.tasks_interfaces import ITaskDispatcher


class CeleryTaskDispatcher(ITaskDispatcher):
    @override
    def dispatch_run(self, run_id: int):
        from fmg.infra.celery.tasks import run_model_task

        run_model_task.delay(run_id)

    @override
    def dispatch_checks(self, run_id: int):
        from fmg.infra.celery.tasks import run_checks_task

        run_checks_task.delay(run_id)
