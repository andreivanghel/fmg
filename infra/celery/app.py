from celery import Celery

celery_app = Celery(
    "central_model_governance_service",
    broker="redis://localhost:6379/0",   # dove sta Redis
    backend="redis://localhost:6379/0"  # dove salva i risultati
)