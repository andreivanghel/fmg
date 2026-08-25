from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from fmg.application.exceptions import ModelNotFoundError, RunNotFoundError
from fmg.application.services.start_run_service import StartRunService
from fmg.domain.entities import ModelRun
from fmg.domain.enums import RunStatus
from fmg.infra.celery.task_dispatcher import CeleryTaskDispatcher
from fmg.infra.django.repositories.run_repository import DjangoRunRepository

# Terminal = the run is done, one way or another. Polling stops once we're here.
TERMINAL_STATUSES = {
    RunStatus.COMPLETED,
    RunStatus.CHECKS_FAILED,
    RunStatus.CHECKS_ERROR,
    RunStatus.FAILED,
}

STAGE_LABELS = ["Pending", "Running", "Outputs", "Checks"]

# Order used to compute how far along the main progress bar a non-terminal run is.
_STAGE_ORDER = [RunStatus.PENDING, RunStatus.RUNNING, RunStatus.OUTPUTS_GENERATED]


def _stage_index(run_status: RunStatus) -> int:
    """0-3: how many of the 4 main stages are 'lit'. Terminal states light all 4."""
    if run_status in TERMINAL_STATUSES:
        return 3
    try:
        return _STAGE_ORDER.index(run_status)
    except ValueError:
        return 0


def _make_repository() -> DjangoRunRepository:
    return DjangoRunRepository()


def run_console(request: HttpRequest) -> HttpResponse:
    """Full page: config panel + empty status/history slots, populated via HTMX."""
    return render(request, "fmg/run_console.html")


def trigger_run(request: HttpRequest) -> HttpResponse:
    """POST from the Run button. Starts a run through the application layer directly
    (StartRunService - same one the DRF API uses) and returns the status fragment,
    which then polls itself via hx-trigger until the run is terminal."""
    try:
        model_id = int(request.POST["model_id"])
        model_version_id = int(request.POST["model_version_id"])
        parameter_version_id = int(request.POST["parameter_version_id"])
    except (KeyError, ValueError):
        return render(
            request,
            "fmg/partials/_error.html",
            {"message": "Missing or invalid model_id / model_version_id / parameter_version_id."},
            status=400,
        )

    service = StartRunService(
        run_repository=_make_repository(), task_dispatcher=CeleryTaskDispatcher()
    )

    try:
        run_id = service.start_run(
            model_id=model_id,
            model_version_id=model_version_id,
            parameter_version_id=parameter_version_id,
        )
    except ModelNotFoundError as e:
        return render(request, "fmg/partials/_error.html", {"message": str(e)}, status=404)

    run = _make_repository().get(run_id)
    return _render_status(request, run)


def run_status(request: HttpRequest, run_id: int) -> HttpResponse:
    """Polled by HTMX every ~400ms until the run reaches a terminal status."""
    try:
        run = _make_repository().get(run_id)
    except RunNotFoundError:
        return render(
            request, "fmg/partials/_error.html", {"message": f"Run {run_id} not found."}, status=404
        )
    return _render_status(request, run)


def _render_status(request: HttpRequest, run: ModelRun) -> HttpResponse:
    idx = _stage_index(run.status)
    is_terminal = run.status in TERMINAL_STATUSES
    stages = [{"label": label, "lit": i <= idx} for i, label in enumerate(STAGE_LABELS)]

    return render(
        request,
        "fmg/partials/_status.html",
        {
            "run": run,
            "stages": stages,
            "is_terminal": is_terminal,
            "is_success": run.status == RunStatus.COMPLETED,
        },
    )


def run_history(request: HttpRequest) -> HttpResponse:
    runs = _make_repository().list_runs(limit=20)
    return render(request, "fmg/partials/_history.html", {"runs": runs})


def run_detail(request: HttpRequest, run_id: int) -> HttpResponse:
    try:
        run = _make_repository().get(run_id)
    except RunNotFoundError:
        return render(
            request, "fmg/partials/_error.html", {"message": f"Run {run_id} not found."}, status=404
        )
    return render(request, "fmg/partials/_detail.html", {"run": run})
