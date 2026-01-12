import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stock

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Stock)
def check_low_stock_after_save(sender, instance, **kwargs):
    if instance.is_low_stock:
        logger.warning(
            f'LOW STOCK WARNING: {instance.product.name} в {instance.location.name}. '
            f'Остаток: {instance.quantity} {instance.product.unit}, минимум: {instance.product.min_stock}'
        )
    
