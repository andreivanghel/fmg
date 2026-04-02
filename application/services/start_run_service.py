from application.interfaces.repositories_interfaces import IRunRepository
from application.interfaces.tasks_interfaces import ITaskDispatcher
from domain.entities import ModelRun

class StartRunService:

    def __init__(
            self, 
            run_repository: IRunRepository, 
            task_dispatcher: ITaskDispatcher
    ) -> None:
        self.run_repository = run_repository
        self.task_dispatcher = task_dispatcher

    ### maybe standardize with def execute for all services
    def start_run(
            self, 
            model_id: int, 
            model_version_id: int,
            parameter_version_id: int
    ) -> str:

        ### manage errors!!!

        run = ModelRun.create(model_id, model_version_id, parameter_version_id)

        saved_run = self.run_repository.save(run)

        self.task_dispatcher.dispatch_run(saved_run.run_id)

        return saved_run.run_id