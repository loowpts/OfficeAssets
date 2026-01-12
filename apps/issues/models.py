from django.db import models
from django.core.exceptions import ValidationError


class Issuance(models.Model):
    inventory_item = models.ForeignKey(
        'assets.Asset',
        on_delete=models.PROTECT,
        related_name='issuances'
    )
    recipient = models.CharField(
        max_length=255,
        verbose_name='Имя получателя'
    )
    issue_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата выдачи'
    )
    return_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата возврата'
    )
    issue_comment = models.TextField(
        blank=True,
        verbose_name='Комментарий при выдаче'
    )
    return_comment = models.TextField(
        blank=True,
        verbose_name='Комментарий при возврате'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Выдача'
        verbose_name_plural = 'Выдачи'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['issue_date']),
        ]
    
    def __str__(self):
        status = 'Возвращена' if self.return_date else 'У сотрудника'
        return f'{self.inventory_item.inventory_number} - {self.recipient} ({status})'
    
    @property 
    def is_returned(self):
        return self.return_date is not None
    
    def clean(self):
        super().clean()

        if self.pk is None:
            active_issue = Issuance.objects.filter(
                inventory_item=self.inventory_item,
                return_date__isnull=True,
            ).first()

            if active_issue:
                raise ValidationError({
                    'inventory_item': (
                        f'Техника {self.inventory_item.inventory_number} '
                        f'уже выдана пользователю {active_issue.recipient}. '
                        f'Дата выдачи: {active_issue.issue_date.strftime("%d.%m.%Y")}'
                    )
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
