import os
from celery import Celery

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fmg.config.settings')

# App initialization
app = Celery(
    "central_model_governance_service",
    broker=os.getenv("CELERY_BROKER_URL", "redis://cmgs_redis:6379/0"),   # Usa env var se c'è, altrimenti localhost
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://cmgs_redis:6379/0"),
    include=['fmg.infra.celery.tasks']
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()