from celery import shared_task


@shared_task
def send_overdue_equipment_reminder():
    """Ежемесячный отчет по списаниям"""
    pass


