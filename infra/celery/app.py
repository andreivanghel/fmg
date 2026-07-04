import os
from celery import Celery

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# App initialization
celery_app = Celery(
    "central_model_governance_service",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),   # Usa env var se c'è, altrimenti localhost
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=['infra.celery.tasks']
)

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()