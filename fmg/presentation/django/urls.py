from django.urls import path

from fmg.presentation.django.views import RunInfoView, RunsView

urlpatterns = [
    path("runs/", RunsView.as_view(), name="start-run"),
    path("runs/<int:run_id>/", RunInfoView.as_view(), name="run-info"),
]
