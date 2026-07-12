from django.urls import path

from fmg.presentation.django.views import RunInfoView, StartRunView

urlpatterns = [
    path("runs/", StartRunView.as_view(), name="start-run"),
    path("runs/<int:run_id>/", RunInfoView.as_view(), name="run-info"),
]
