from infra.celery.app import app
from application.services.run_model_service import RunModelService
from application.services.run_checks_service import RunChecksService
from application.factories.model_factory import ModelFactory
from infra.django.repositories.run_repository import DjangoRunRepository
from infra.django.repositories.parameters_repository import DjangoParametersRepository
from infra.celery.task_dispatcher import CeleryTaskDispatcher


@app.task
def run_model_task(run_id: int):

    # TODO: Adopt dependency injection AS SOON AS POSSIBLE. (--> composition root)
    run_repository = DjangoRunRepository()
    parameters_repository = DjangoParametersRepository()
    model_factory = ModelFactory()
    task_dispatcher = CeleryTaskDispatcher()

    service = RunModelService(
        run_repository=run_repository,
        parameters_repository=parameters_repository,
        model_factory=model_factory,
        task_dispatcher=task_dispatcher
    )

    service.run_model(run_id)


@app.task
def run_checks_task(run_id: int):

    # TODO: Adopt dependency injection AS SOON AS POSSIBLE. (--> composition root)
    run_repository = DjangoRunRepository()
    model_factory = ModelFactory()
    task_dispatcher = CeleryTaskDispatcher()

    service = RunChecksService(
        run_repository=run_repository,
        model_factory=model_factory,
        task_dispatcher=task_dispatcher
    )

    service.run_checks(run_id)