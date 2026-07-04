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

        run_id = self.run_repository.create(run)

        self.task_dispatcher.dispatch_run(run_id) # TODO: Race condition: if the task is executed before the transaction is committed, the run will not be found in the database. ( do We need to use an outbox pattern to avoid this. (?))

        return run_id
