from fmg.application.factories.model_factory import ModelFactory
from fmg.application.interfaces.repositories_interfaces import IParametersRepository, IRunRepository
from fmg.application.interfaces.tasks_interfaces import ITaskDispatcher
from fmg.domain.enums import RunStatus

### TO BE REFACTORED (concurrency, transaction boundaries, error handling, protected dispatch checks)


class RunModelService:
    def __init__(
        self,
        run_repository: IRunRepository,
        parameters_repository: IParametersRepository,
        model_factory: ModelFactory,
        task_dispatcher: ITaskDispatcher,
    ):
        self.run_repository = run_repository
        self.parameters_repository = parameters_repository
        self.model_factory = model_factory
        self.task_dispatcher = task_dispatcher

    def run_model(self, run_id: int) -> None:

        ### CONCURRENCY!!!
        run = self.run_repository.get(run_id)
        if run.status != RunStatus.PENDING:
            return

        running_run = run.mark_as_running()
        self.run_repository.save(running_run)

        # TODO: If an error occurs before try final_run is never defined, so we need to handle that case
        # final_run = None
        try:
            model = self.model_factory.get(running_run.model_id, running_run.model_version_id)
            parameters = self.parameters_repository.get(running_run.parameter_version_id)

            parameter_set = parameters.parameter_set

            outputs = model.run(parameter_set)
            final_run = running_run.apply_outputs(outputs)

        ### we need more granular error signaling
        except Exception as e:
            ### add logger
            final_run = running_run.mark_as_failed(str(e))

        finally:
            try:
                self.run_repository.save(final_run)

            except Exception:
                # logging
                raise
        ### we need ATOMICITY! --> outbox pattern
        if final_run.run_id is None:
            raise ValueError(
                f"Run {run_id} is inconsistent: null run_id after persistence — domain invariant violated"
            )

        if final_run.status == RunStatus.OUTPUTS_GENERATED:
            self.task_dispatcher.dispatch_checks(final_run.run_id)
