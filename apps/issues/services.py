import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Issuance
from apps.references.models import Location
from apps.assets.models import Asset
from apps.core.exceptions import AssetNotAvailableError

logger = logging.getLogger(__name__)

class IssuancesService:
    
    @staticmethod
    @transaction.atomic
    def create_issuance(inventory_item: Asset, recipient: str, comment: str = '') -> Issuance:

        if not inventory_item.is_available:
            raise AssetNotAvailableError(
                f'Техника {inventory_item.inventory_number} недоступна. '
                f'Текущий статус: {inventory_item.get_status_display()}'
            )
        
        active_issue = Issuance.objects.filter(
            inventory_item=inventory_item,
            return_date__isnull=True
        ).first()
        
        if active_issue:
            raise AssetNotAvailableError(
                f'Техника {inventory_item.inventory_number} уже выдана '
                f'пользователю {active_issue.recipient} '
                f'({active_issue.issue_date.strftime("%d.%m.%Y")})'
            )
        
        issuance = Issuance.objects.create(
            inventory_item=inventory_item,
            recipient=recipient,
            issue_comment=comment
        )
        
        inventory_item.mark_as_issued()
        
        logger.info(
            f'Создана выдача #{issuance.id}: '
            f'{inventory_item.inventory_number} → {recipient}'
        )
        
        return issuance
        
    
    @staticmethod
    @transaction.atomic
    def create_return(issuance: Issuance, location: Location, comment: str = '') -> Issuance:
        
        if issuance.is_returned:
            raise ValidationError(
                f'Техника {issuance.inventory_item.inventory_number} '
                f'уже возвращена {issuance.return_date.strftime("%d.%m.%Y")}'
            )
            
        issuance.return_date = timezone.now()
        issuance.return_comment = comment
        issuance.save()
        
        inventory_item = issuance.inventory_item
        inventory_item.mark_as_returned()
        inventory_item.current_location = location
        inventory_item.save()
        
        logger.info(
            f'Возврат выдачи #{issuance.id}: '
            f'{inventory_item.inventory_number} от {issuance.recipient} '
            f'→ {location.name}'
        )
        
        return issuance
        
    @staticmethod
    def get_active_issuances():
        return Issuance.objects.filter(
            return_date__isnull=True
        ).select_related('inventory_item', 'inventory_item__product')
        
    @staticmethod
    def get_issuances_by_recipient(recipient: str):
        return Issuance.objects.filter(
            recipient__icontains=recipient
        ).select_related('inventory_item')
            
