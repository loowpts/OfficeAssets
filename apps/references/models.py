from django.db import models
from slugify import slugify


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True)
        
    def __str__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locations'
        verbose_name = 'Местоположения'
        verbose_name_plural = 'Местоположении'
        
    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True)

    def __str__(self):
        return self.name
