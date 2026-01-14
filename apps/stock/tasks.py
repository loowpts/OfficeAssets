from celery import shared_task


@shared_task
def check_low_stock():
    """Проверка низких остатков и отправка уведомлений"""
    pass

@shared_task
def generate_stock_report():
    """Генерация ежедневного отчета по остаткам на складе"""
    pass


