from celery import Celery
from .config import settings

celery = Celery("Choice_tasks",
                   backend=settings.REDIS_URL,
                   broker=settings.REDIS_URL)

celery.autodiscover_tasks([".tasks"])