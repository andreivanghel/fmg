import traceback

from fmg.application.factories.model_factory import ModelFactory
from fmg.application.interfaces.repositories_interfaces import IRunRepository
from fmg.application.interfaces.tasks_interfaces import ITaskDispatcher
from fmg.domain.enums import RunStatus


class RunChecksService:
    def __init__(
        self,
        run_repository: IRunRepository,
        model_factory: ModelFactory,
        task_dispatcher: ITaskDispatcher,  # for actions tasks!
    ):
        self.run_repository = run_repository
        self.model_factory = model_factory
        self.task_dispatcher = task_dispatcher

    def run_checks(self, run_id: int) -> None:
        print(f"Running checks for run_id: {run_id}")
        run = self.run_repository.get(run_id)
        if run.status != RunStatus.OUTPUTS_GENERATED:
            ### logging?
            return

        if run.outputs is None:
            run = run.mark_as_checks_error(
                "Invariant violated: status OUTPUTS_GENERATED but outputs is None"
            )
            self.run_repository.save(run)
            return

        try:
            model = self.model_factory.get(run.model_id, run.model_version_id)
            check_results = model.run_checks(run.outputs)
            print(f"Outputs: {run.outputs}")
            print(f"Check results: {check_results}")
            final_run = run.apply_checks(check_results)

        except Exception as e:
            traceback.print_exc()
            final_run = run.mark_as_checks_error(str(e))

        finally:
            self.run_repository.save(final_run)
