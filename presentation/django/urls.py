from django.urls import path
from presentation.django.views import StartRunView, RunInfoView

urlpatterns = [
    path("runs/", StartRunView.as_view(), name="start-run"),
    path("runs/<int:run_id>/", RunInfoView.as_view(), name="run-info"),
]