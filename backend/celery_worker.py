from celery import Celery
from config import Config

def make_celery(app=None):
    """Create / bind a Celery instance to Flask app (app optional)."""
    celery = Celery(
        "curevox",
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
    )
    # load config from flask app if provided
    if app is not None:
        celery.conf.update(app.config.get('CELERY', {}) or {})
    celery.conf.update(task_serializer='json', result_serializer='json', accept_content=['json'])
    return celery

# Create a celery instance for imports
celery = make_celery()
@celery.task(bind=True)
def generate_report_task(self, user_id, report_data):
    from services.report_service import generate_pdf_report
    pdf_path = generate_pdf_report(user_id, report_data)
    return {"pdf": pdf_path}
