from application.interfaces.repositories_interfaces import IRunRepository
from application.interfaces.tasks_interfaces import ITaskDispatcher
from domain.entities import ModelRun

class StartRunService:

    def __init__(self, run_repository: IRunRepository, task_dispatcher: ITaskDispatcher):
        self.run_repository = run_repository
        self.task_dispatcher = task_dispatcher

    def start_run(
            self, 
            model_id: str, 
            model_version: str,
            parameters_version: str
    ) -> str:

        ### manage errors!!!

        run = ModelRun.create(model_id, model_version, parameters_version)

        self.run_repository.save(run) ### deve restituire una nuova istanza di ModelRun!!! aggiornata. è frozen

        self.task_dispatcher.dispatch_run(run.id)

        return run.id