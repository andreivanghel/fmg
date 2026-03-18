from application.interfaces.repositories_interfaces import IRunRepository, IParametersRepository
from application.interfaces.tasks_interfaces import ITaskDispatcher
from application.factories.model_factory import ModelFactory
from domain.enums import RunStatus


class RunModelService:

    def __init__(
            self, 
            run_repository: IRunRepository, 
            parameters_repository: IParametersRepository, 
            model_factory: ModelFactory,
            task_dispatcher: ITaskDispatcher
    ):
        self.run_repository = run_repository
        self.parameters_repository = parameters_repository
        self.model_factory = model_factory
        self.task_dispatcher = task_dispatcher


    def run_model(
            self, 
            run_id: str
    ) -> None:

        run = self.run_repository.get(run_id)
        if run.status != RunStatus.PENDING:
            return

        run.mark_as_running()
        self.run_repository.save(run)

        try:
            model = self.model_factory.get(run.model_id, run.model_version)
            parameters = self.parameters_repository.get(run.model_id, run.parameters_version)

            outputs = model.run(parameters)
            run.mark_as_outputs_generated(outputs)

        except Exception as e:
            ### add logger
            run.mark_as_failed(str(e))
            
        finally: 
            try:
                self.run_repository.save(run)

            except Exception:
                #logging
                raise

        if run.status == RunStatus.OUTPUTS_GENERATED:
            self.task_dispatcher.dispatch_checks(run.id)
