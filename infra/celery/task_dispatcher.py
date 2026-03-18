from application.interfaces.tasks_interfaces import ITaskDispatcher

class CeleryTaskDispatcher(ITaskDispatcher):

    def dispatch_run(self, run_id: str):
        from infra.celery.tasks import run_model_task
        run_model_task.delay(run_id)
        
    def dispatch_checks(self, run_id: str):
        from infra.celery.tasks import run_checks_task
        run_checks_task.delay(run_id)