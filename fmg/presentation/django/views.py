from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from fmg.application.exceptions import ModelNotFoundError, RunNotFoundError
from fmg.application.services.start_run_service import StartRunService
from fmg.infra.celery.task_dispatcher import CeleryTaskDispatcher
from fmg.infra.django.repositories.run_repository import DjangoRunRepository
from fmg.presentation.django.serializers import (
    RunIdSerializer,
    RunInfoSerializer,
    StartRunRequestSerializer,
)


class StartRunView(APIView):
    def _make_service(
        self,
    ) -> StartRunService:  # NOTE: this should be placed in a composition root...
        return StartRunService(
            run_repository=DjangoRunRepository(), task_dispatcher=CeleryTaskDispatcher()
        )

    def post(self, request: Request) -> Response:
        # Input validation
        serializer = StartRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Service call
        service = self._make_service()

        try:
            run_id = service.start_run(
                model_id=data["model_id"],
                model_version_id=data["model_version_id"],
                parameter_version_id=data["parameter_version_id"],
            )

        except ModelNotFoundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        # Output serialization
        response = RunIdSerializer({"run_id": run_id})

        return Response(data=response.data, status=status.HTTP_202_ACCEPTED)


class RunInfoView(APIView):
    def _make_repository(self):
        return DjangoRunRepository()

    def get(self, request: Request, run_id: int) -> Response:
        # Get data from DB
        run_repository = self._make_repository()
        run = run_repository.get(run_id)

        try:
            run = run_repository.get(run_id)
        except RunNotFoundError:
            return Response(
                {"detail": f"Run '{run_id}' not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Output serialization
        response = RunInfoSerializer(run)

        return Response(data=response.data, status=status.HTTP_200_OK)
