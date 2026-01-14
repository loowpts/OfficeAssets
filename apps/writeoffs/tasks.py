from celery import shared_task


@shared_task
def generate_writeoff_report():
    """Генерация ежеквартального отчета по списаниям"""
    pass
