from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from application.services.start_run_service import StartRunService
from application.exceptions import ModelNotFoundError
from infra.django.repositories.run_repository import DjangoRunRepository
from infra.celery.task_dispatcher import CeleryTaskDispatcher
from presentation.django.serializers import StartRunRequestSerializer, StartRunResponseSerializer, RunInfoSerializer


class StartRunView(APIView):

    def _make_service(self) -> StartRunService: # NOTE: this should be placed in a composition root...
        return StartRunService(
            run_repository = DjangoRunRepository(),
            task_dispatcher = CeleryTaskDispatcher()
        )
    
    def post(self, request: Request) -> Response:
        # Input validation
        serializer = StartRunRequestSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Service call
        service = self._make_service()
        run = service.start_run(
            model_id = data["model_id"],
            model_version = data["model_version"],
            parameters_version = data["parameters_version"]
        )

        # Output serialization
        response = StartRunResponseSerializer(run)
        
        return Response(
            data = response.data,
            status = status.HTTP_202_ACCEPTED
        )


class RunInfoView(APIView):

    def _make_service(self):
        return DjangoRunRepository()
    
    def get(self, request: Request, run_id: str) -> Response:
        # Get data from DB
        run_repository = self._make_service()
        run = run_repository.get(run_id)

        # Output serialization
        response = RunInfoSerializer(run)

        return Response(
            data = response.data,
            status = status.HTTP_200_OK
        )