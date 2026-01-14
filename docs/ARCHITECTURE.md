# Архитектура системы OfficeAssets

## Содержание
- [Общий обзор](#общий-обзор)
- [Слои приложения](#слои-приложения)
- [Модули и их взаимодействие](#модули-и-их-взаимодействие)
- [Паттерны проектирования](#паттерны-проектирования)
- [Потоки данных](#потоки-данных)
- [Безопасность](#безопасность)
- [Масштабируемость](#масштабируемость)

---

## Общий обзор

OfficeAssets построен на основе многослойной архитектуры с четким разделением ответственности.

```
┌───────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
│                 (REST API + Swagger UI)                    │
└─────────────────────────┬─────────────────────────────────┘
                          │
                          │ HTTP/JSON
                          ▼
┌───────────────────────────────────────────────────────────┐
│                    API Layer (Views)                       │
│              Django REST Framework ViewSets                │
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Serializers │  │ Permissions │  │   Filters   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────┬─────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                   Business Logic Layer                     │
│                       (Services)                           │
│                                                            │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  StockService    │  │ IssuanceService  │              │
│  │  - receipt()     │  │ - create()       │              │
│  │  - expense()     │  │ - return()       │              │
│  │  - transfer()    │  │ - get_active()   │              │
│  └──────────────────┘  └──────────────────┘              │
│                                                            │
│  ┌──────────────────┐                                     │
│  │ WriteOffService  │                                     │
│  │ - write_off_...  │                                     │
│  └──────────────────┘                                     │
└─────────────────────────┬─────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                    Data Access Layer                       │
│                     (Django ORM)                           │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │  Models  │  │ Managers │  │QuerySets │  │Validators││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────┬─────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                    Database Layer                          │
│              PostgreSQL / SQLite3                          │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                   Background Services                      │
│                Celery Workers + Beat                       │
│                                                            │
│  ┌────────────────┐              ┌────────────────┐      │
│  │ check_low_stock│              │ generate_report│      │
│  │   (daily)      │              │   (monthly)    │      │
│  └────────────────┘              └────────────────┘      │
└───────────────────────────────────────────────────────────┘
                          ▲
                          │
                     Redis Queue
```

---

## Слои приложения

### 1. Presentation Layer (Представление)

**Ответственность:**
- REST API endpoints
- Сериализация/десериализация данных
- API документация (Swagger)

**Технологии:**
- Django REST Framework
- drf-spectacular (OpenAPI)

### 2. API Layer (Представление данных)

**Компоненты:**
- **ViewSets**: Обработка HTTP запросов
- **Serializers**: Преобразование данных
- **Permissions**: Контроль доступа
- **Filters**: Фильтрация и поиск

**Пример:**
```python
# apps/stock/views.py
class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related('product', 'location')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['product', 'location']
```

### 3. Business Logic Layer (Бизнес-логика)

**Ответственность:**
- Валидация бизнес-правил
- Транзакционные операции
- Координация между моделями

**Сервисы:**
```python
# apps/stock/services.py
class StockService:
    @transaction.atomic
    def create_receipt(product, quantity, to_location, comment):
        # Бизнес-логика прихода товара
        pass

    @transaction.atomic
    def create_expense(product, quantity, from_location, comment):
        # Валидация достаточности остатков
        # Уменьшение количества
        pass
```

### 4. Data Access Layer (Доступ к данным)

**Компоненты:**
- **Models**: Определение структуры данных
- **Managers**: Кастомные запросы
- **QuerySets**: Оптимизация запросов
- **Validators**: Валидация на уровне модели

**Пример:**
```python
# apps/assets/models.py
class Asset(models.Model):
    # ... поля ...

    def clean(self):
        """Валидация на уровне модели"""
        if self.status == 'issued' and not self.recipient:
            raise ValidationError("Issued asset must have recipient")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

### 5. Database Layer (База данных)

**Ответственность:**
- Хранение данных
- Обеспечение целостности
- Индексы и оптимизация

---

## Модули и их взаимодействие

### Схема взаимодействия модулей

```
┌─────────────┐
│ References  │ (Справочники)
│             │
│ - Category  │◄─────┐
│ - Location  │◄───┐ │
└─────────────┘    │ │
                   │ │
                   │ │ FK
┌─────────────┐    │ │
│  Products   │────┘ │
│             │      │
│ - Product   │      │
└──────┬──────┘      │
       │             │
       │ is_consumable?
       │             │
       ├─────────────┴──────┐
       │                    │
       ▼ False              ▼ True
┌─────────────┐      ┌─────────────┐
│   Assets    │      │    Stock    │
│             │      │             │
│ - Asset     │      │ - Stock     │
│             │      │ - StockOper │
└──────┬──────┘      └──────┬──────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│   Issues    │      │  WriteOffs  │
│             │      │             │
│ - Issuance  │      │ - WriteOff  │
└─────────────┘      └─────────────┘
       │                    │
       └────────┬───────────┘
                ▼
         ┌─────────────┐
         │    Core     │
         │             │
         │ Exceptions  │
         └─────────────┘
```

### Зависимости между модулями

```python
# Зависимости (импорты)

References (нет зависимостей)
    ↓
Products (зависит от References)
    ↓
Assets, Stock (зависят от Products, References)
    ↓
Issues, WriteOffs (зависят от Assets, Stock, Products)
    ↓
Core (используется всеми)
```

---

## Паттерны проектирования

### 1. Service Layer Pattern

**Проблема:** Бизнес-логика не должна быть в Views или Models

**Решение:** Вынос бизнес-логики в отдельные Service классы

```python
# apps/stock/services.py
class StockService:
    """Сервис управления складскими операциями"""

    @staticmethod
    @transaction.atomic
    def create_receipt(product, quantity, to_location, comment=""):
        """Приход товара на склад"""

        # Создание операции
        operation = StockOperations.objects.create(
            product=product,
            operation_type='receipt',
            quantity=quantity,
            to_location=to_location,
            comment=comment
        )

        # Обновление остатков
        stock, created = Stock.objects.get_or_create(
            product=product,
            location=to_location,
            defaults={'quantity': 0}
        )
        stock.quantity += quantity
        stock.save()

        return operation
```

**Преимущества:**
- Переиспользование логики
- Легко тестировать
- Единая точка изменения

### 2. Repository Pattern (через Django ORM)

**Проблема:** Прямой доступ к базе данных из бизнес-логики

**Решение:** Использование Django Managers и QuerySets

```python
# apps/stock/managers.py
class StockManager(models.Manager):
    def low_stock(self):
        """Товары с низким остатком"""
        return self.select_related('product', 'location').filter(
            quantity__lte=F('product__min_stock')
        )

    def by_location(self, location):
        """Остатки на конкретной локации"""
        return self.filter(location=location)

# Использование
Stock.objects.low_stock()
```

### 3. Factory Pattern (для создания сложных объектов)

```python
# apps/assets/factories.py
class AssetFactory:
    @staticmethod
    def create_asset(product, serial_number, inventory_number, location):
        """Создание актива с валидацией"""
        if product.is_consumable:
            raise ValueError("Cannot create asset for consumable product")

        asset = Asset(
            product=product,
            serial_number=serial_number,
            inventory_number=inventory_number,
            current_location=location,
            status='in_stock'
        )
        asset.full_clean()
        asset.save()
        return asset
```

### 4. State Pattern (для статусов)

```python
# apps/assets/models.py
class Asset(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'В наличии'),
        ('issued', 'Выдана'),
        ('maintenance', 'На обслуживании'),
        ('written_off', 'Списана'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def mark_as_issued(self):
        """Переход в состояние 'Выдана'"""
        if self.status != 'in_stock':
            raise AssetNotAvailableError("Asset must be in stock")
        self.status = 'issued'
        self.save()

    def mark_as_returned(self):
        """Возврат в состояние 'В наличии'"""
        if self.status != 'issued':
            raise ValidationError("Only issued assets can be returned")
        self.status = 'in_stock'
        self.save()
```

### 5. Observer Pattern (через Django Signals)

```python
# apps/stock/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Stock)
def check_low_stock_alert(sender, instance, **kwargs):
    """Уведомление при низком остатке"""
    if instance.is_low_stock():
        # Отправить уведомление
        logger.warning(f"Low stock alert: {instance.product.name}")
```

### 6. Strategy Pattern (для разных типов операций)

```python
# apps/stock/strategies.py
class StockOperationStrategy:
    def execute(self, product, quantity, **kwargs):
        raise NotImplementedError

class ReceiptStrategy(StockOperationStrategy):
    def execute(self, product, quantity, to_location, comment=""):
        return StockService.create_receipt(product, quantity, to_location, comment)

class ExpenseStrategy(StockOperationStrategy):
    def execute(self, product, quantity, from_location, comment=""):
        return StockService.create_expense(product, quantity, from_location, comment)
```

---

## Потоки данных

### Поток 1: Приход товара на склад

```
┌──────────┐
│ REST API │ POST /api/v1/stock-operation/receipt/
└────┬─────┘
     │ {product: 1, quantity: 50, to_location: 1}
     ▼
┌──────────────────┐
│ ViewSet          │ StockOperationViewSet.create_receipt()
│ (API Layer)      │
└────┬─────────────┘
     │ Валидация через Serializer
     ▼
┌──────────────────┐
│ Service          │ StockService.create_receipt()
│ (Business Logic) │
└────┬─────────────┘
     │ @transaction.atomic
     │
     ├──► 1. Создать StockOperations (operation_type='receipt')
     │
     └──► 2. Обновить/Создать Stock
          │
          ├─ Найти Stock(product=1, location=1)
          │  ├─ Если существует: quantity += 50
          │  └─ Если нет: создать с quantity = 50
          │
          └─ Сохранить изменения

┌──────────────────┐
│ Database         │
│                  │
│ StockOperations  │ +1 запись
│ Stock            │ +50 quantity
└──────────────────┘
```

### Поток 2: Выдача техники сотруднику

```
┌──────────┐
│ REST API │ POST /api/v1/issues/create_issuance/
└────┬─────┘
     │ {inventory_item: 1, recipient: "Иванов И.И."}
     ▼
┌──────────────────┐
│ ViewSet          │ IssuanceViewSet.create_issuance()
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Service          │ IssuanceService.create_issuance()
└────┬─────────────┘
     │ @transaction.atomic
     │
     ├──► 1. Проверить Asset.status == 'in_stock'
     │    │  └─ Если нет → raise AssetNotAvailableError
     │    │
     │    ▼
     ├──► 2. Создать Issuance
     │    │  - inventory_item = asset
     │    │  - recipient = "Иванов И.И."
     │    │  - issue_date = today
     │    │  - return_date = null
     │    │
     │    ▼
     └──► 3. Обновить Asset
          │  - status = 'issued'
          └─ Сохранить

┌──────────────────┐
│ Database         │
│                  │
│ Issuance         │ +1 запись
│ Asset            │ status='issued'
└──────────────────┘
```

### Поток 3: Списание расходника

```
┌──────────┐
│ REST API │ POST /api/v1/writeoffs/create_consumable/
└────┬─────┘
     │ {product: 1, quantity: 5, location: 1, reason: "..."}
     ▼
┌──────────────────┐
│ ViewSet          │ WriteOffViewSet.create_consumable()
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Service          │ WriteOffService.create_writeoff_consumable()
└────┬─────────────┘
     │ @transaction.atomic
     │
     ├──► 1. Найти Stock(product=1, location=1)
     │    │  └─ Если нет → raise ValidationError
     │    │
     │    ▼
     ├──► 2. Проверить количество
     │    │  └─ Если stock.quantity < 5 → raise InsufficientStockError
     │    │
     │    ▼
     ├──► 3. Создать WriteOff
     │    │  - product = product
     │    │  - quantity = 5
     │    │  - location = location
     │    │  - reason = reason
     │    │
     │    ▼
     └──► 4. Уменьшить Stock.quantity -= 5
          └─ Сохранить

┌──────────────────┐
│ Database         │
│                  │
│ WriteOff         │ +1 запись
│ Stock            │ quantity -= 5
└──────────────────┘
```

---

## Безопасность

### Аутентификация

```
┌──────────────────────────────────────────────────┐
│              JWT Token Authentication             │
└──────────────────────────────────────────────────┘

Клиент                          Сервер
   │                               │
   │ POST /api/token/              │
   │ {username, password}          │
   ├──────────────────────────────►│
   │                               │ Валидация credentials
   │                               │
   │ {access, refresh}             │
   │◄──────────────────────────────┤
   │                               │
   │ GET /api/v1/products/         │
   │ Authorization: Bearer {token} │
   ├──────────────────────────────►│
   │                               │ Проверка JWT
   │                               │ IsAuthenticated?
   │ {products data}               │
   │◄──────────────────────────────┤
   │                               │
   │ Token истек через 15 мин      │
   │                               │
   │ POST /api/token/refresh/      │
   │ {refresh}                     │
   ├──────────────────────────────►│
   │                               │
   │ {access}                      │
   │◄──────────────────────────────┤
```

### Уровни защиты

1. **Transport Security**
   - HTTPS в production
   - Secure cookies

2. **Authentication**
   - JWT токены
   - Token expiration (15 минут для access, 1 день для refresh)

3. **Authorization**
   - Permission classes на ViewSet уровне
   - `IsAuthenticated` - требует авторизации

4. **Input Validation**
   - Serializers для валидации входных данных
   - Model.clean() для бизнес-правил
   - Database constraints

5. **SQL Injection Prevention**
   - Django ORM (параметризованные запросы)
   - Никогда не используем raw SQL с пользовательским вводом

6. **XSS Prevention**
   - API только JSON (не HTML)
   - Клиент отвечает за санитизацию

---

## Масштабируемость

### Горизонтальное масштабирование

```
                    ┌──────────────┐
                    │ Load Balancer│
                    │   (Nginx)    │
                    └───────┬──────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Django   │      │ Django   │      │ Django   │
    │ Instance │      │ Instance │      │ Instance │
    │    #1    │      │    #2    │      │    #3    │
    └────┬─────┘      └────┬─────┘      └────┬─────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
    ┌──────────┐                       ┌──────────┐
    │PostgreSQL│                       │  Redis   │
    │ (Primary)│                       │  Cache   │
    └────┬─────┘                       └──────────┘
         │
         ▼
    ┌──────────┐
    │PostgreSQL│
    │(Replica) │
    └──────────┘

┌────────────────────────────────────────────────┐
│           Celery Workers                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Worker 1 │  │ Worker 2 │  │ Worker 3 │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┼──────────────┘          │
└─────────────────────┼─────────────────────────┘
                      │
                      ▼
                 ┌──────────┐
                 │  Redis   │
                 │  Queue   │
                 └──────────┘
```

### Оптимизация запросов

**Проблема N+1:**
```python
# Плохо - N+1 запросов
for asset in Asset.objects.all():
    print(asset.product.name)  # Запрос для каждого asset

# Хорошо - 1 запрос
for asset in Asset.objects.select_related('product'):
    print(asset.product.name)
```

**Prefetch для Many-to-Many:**
```python
# apps/products/views.py
class ProductViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Product.objects.prefetch_related(
            'assets',
            'stock_set'
        ).select_related('category')
```

### Кэширование

```python
# settings/settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Использование
from django.core.cache import cache

def get_low_stock_items():
    key = 'low_stock_items'
    items = cache.get(key)

    if items is None:
        items = Stock.objects.low_stock()
        cache.set(key, items, 300)  # 5 минут

    return items
```

### Database индексы

```python
# apps/stock/models.py
class StockOperations(models.Model):
    # ...

    class Meta:
        indexes = [
            models.Index(fields=['product', 'timestamp']),
            models.Index(fields=['operation_type', 'timestamp']),
            models.Index(fields=['-timestamp']),
        ]
```

### Pagination

```python
# settings/settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

---

## Мониторинг и логирование

### Структура логов

```python
# settings/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.stock': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Метрики для мониторинга

1. **Performance метрики:**
   - Response time для API endpoints
   - Database query time
   - Cache hit rate

2. **Business метрики:**
   - Количество операций в день
   - Низкие остатки
   - Активные выдачи техники

3. **System метрики:**
   - CPU/Memory usage
   - Celery queue length
   - Database connections

---

## Тестирование

### Структура тестов

```
apps/
└── stock/
    ├── tests/
    │   ├── __init__.py
    │   ├── test_models.py      # Unit тесты моделей
    │   ├── test_services.py    # Unit тесты сервисов
    │   ├── test_views.py       # API тесты
    │   └── test_integration.py # Интеграционные тесты
```

### Пример теста

```python
# apps/stock/tests/test_services.py
import pytest
from apps.stock.services import StockService
from apps.core.exceptions import InsufficientStockError

@pytest.mark.django_db
class TestStockService:
    def test_create_receipt_increases_quantity(self, product, location):
        """Приход товара увеличивает остаток"""
        initial_quantity = 10
        Stock.objects.create(
            product=product,
            location=location,
            quantity=initial_quantity
        )

        StockService.create_receipt(product, 50, location)

        stock = Stock.objects.get(product=product, location=location)
        assert stock.quantity == initial_quantity + 50

    def test_create_expense_insufficient_stock(self, product, location):
        """Расход больше остатка вызывает ошибку"""
        Stock.objects.create(
            product=product,
            location=location,
            quantity=5
        )

        with pytest.raises(InsufficientStockError):
            StockService.create_expense(product, 10, location)
```

---

## Будущие улучшения

### Планируемые функции

1. **Real-time уведомления** (WebSocket)
2. **Экспорт в Excel/PDF**
3. **QR коды для техники**
4. **Мобильное приложение**
5. **Аналитика и отчеты**
6. **Интеграция с 1C**
7. **Role-based access control**
8. **История изменений (Audit log)**

### Технический долг

- [ ] Добавить comprehensive тесты (coverage > 80%)
- [ ] Настроить CI/CD pipeline
- [ ] Добавить rate limiting
- [ ] Настроить monitoring (Prometheus + Grafana)
- [ ] Оптимизировать сложные запросы
- [ ] Добавить API versioning
- [ ] Документировать все endpoints в Swagger

---

## Заключение

Архитектура OfficeAssets спроектирована с учетом:
- **Модульности**: Каждый модуль независим
- **Масштабируемости**: Легко добавлять новые instance
- **Поддерживаемости**: Четкое разделение ответственности
- **Тестируемости**: Service layer легко тестировать
- **Безопасности**: JWT + validation на всех уровнях

Система готова к production развертыванию и дальнейшему развитию.
