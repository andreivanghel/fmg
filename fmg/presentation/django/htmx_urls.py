from django.urls import path

from fmg.presentation.django import htmx_views

urlpatterns = [
    path("", htmx_views.run_console, name="run-console"),
    path("runs/trigger/", htmx_views.trigger_run, name="htmx-trigger-run"),
    path("runs/<int:run_id>/status/", htmx_views.run_status, name="htmx-run-status"),
    path("runs/<int:run_id>/detail/", htmx_views.run_detail, name="htmx-run-detail"),
    path("runs/history/", htmx_views.run_history, name="htmx-run-history"),
]
