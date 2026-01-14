# OfficeAssets - Система управления офисным имуществом

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.5-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**OfficeAssets** — это комплексная система учета и управления офисным имуществом, построенная на Django REST Framework. Система предоставляет полный контроль над техникой и расходными материалами: от поступления на склад до списания.

## Содержание

- [Основные возможности](#основные-возможности)
- [Быстрый старт](#быстрый-старт)
- [Архитектура системы](#архитектура-системы)
- [Технологический стек](#технологический-стек)
- [Структура базы данных](#структура-базы-данных)
- [Установка и настройка](#установка-и-настройка)
- [API документация](#api-документация)
- [Бизнес-процессы](#бизнес-процессы)
- [Автоматизация](#автоматизация)
- [Разработка](#разработка)
- [Дополнительная документация](#дополнительная-документация)
- [Поддержка](#поддержка)

---

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yourusername/OfficeAssets.git
cd OfficeAssets

# 2. Создать виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env файл

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver
```

Приложение доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

API документация: [http://127.0.0.1:8000/api/v1/docs/](http://127.0.0.1:8000/api/v1/docs/)

---

## Основные возможности

### Управление техникой (Assets)
- Учет каждой единицы техники с уникальным инвентарным номером
- Отслеживание статусов: В наличии → Выдана → На обслуживании → Списана
- История выдачи и возврата техники сотрудникам
- Контроль местоположения техники

### Управление расходниками (Consumables)
- Количественный учет расходных материалов на складах
- Операции прихода, расхода и перемещения товаров
- Автоматический контроль минимальных остатков
- История всех складских операций

### Справочники и категоризация
- Управление категориями товаров
- Множественные локации (склады, офисы, кабинеты)
- Гибкая система единиц измерения

### Списание и аудит
- Списание техники с указанием причины
- Списание расходников по количеству
- Полная история операций для аудита
- Автоматическая генерация отчетов

---

## Архитектура системы

### Общая структура приложения

```
┌─────────────────────────────────────────────────────────────┐
│                      REST API Layer                         │
│              (Django REST Framework + JWT)                  │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │References  │  │ Products │  │  Assets  │  │  Stock   │ │
│  │(Справочн.) │  │ (Товары) │  │ (Техника)│  │(Остатки) │ │
│  └────────────┘  └──────────┘  └──────────┘  └──────────┘ │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐                │
│  │  Issues    │  │WriteOffs │  │   Core   │                │
│  │  (Выдача)  │  │(Списание)│  │  (Ядро)  │                │
│  └────────────┘  └──────────┘  └──────────┘                │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    Service Layer                             │
│   ┌─────────────────┐  ┌──────────────────┐                │
│   │  StockService   │  │ IssuancesService │                │
│   │  - Приход       │  │ - Выдача техники │                │
│   │  - Расход       │  │ - Возврат        │                │
│   │  - Перемещение  │  └──────────────────┘                │
│   └─────────────────┘  ┌──────────────────┐                │
│                        │ WriteOffService  │                │
│                        │ - Списание       │                │
│                        └──────────────────┘                │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    Database Layer                            │
│                   PostgreSQL / SQLite3                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   Background Tasks                           │
│           Celery + Redis + Celery Beat                       │
│   - Проверка низких остатков (ежедневно)                    │
│   - Генерация отчетов (ежемесячно)                          │
└──────────────────────────────────────────────────────────────┘
```

### Модульная структура

```
apps/
├── references/     # Справочники (Categories, Locations)
├── products/       # Каталог товаров и техники
├── assets/         # Управление техникой (инвентарь)
├── stock/          # Остатки и операции с расходниками
├── issues/         # Выдача и возврат техники
├── writeoffs/      # Списание техники и расходников
└── core/           # Общие компоненты и исключения
```

---

## Технологический стек

### Backend
- **Framework**: Django 5.2.5
- **API**: Django REST Framework 3.16.1
- **Authentication**: Simple JWT 5.5.1
- **API Documentation**: drf-spectacular 0.27.1 (OpenAPI 3.0)

### Database
- **Development**: SQLite3
- **Production**: PostgreSQL (psycopg2-binary 2.9.9)

### Task Queue & Scheduling
- **Task Queue**: Celery 5.5.3
- **Scheduler**: django-celery-beat 2.8.1
- **Message Broker**: Redis 6.4.0

### Additional
- **Caching**: django-redis 5.4.0
- **CORS**: django-cors-headers 4.7.0
- **Configuration**: python-decouple 3.8
- **WSGI Server**: Gunicorn 23.0.0
- **Image Processing**: Pillow 11.3.0

---

## Структура базы данных

### ER-диаграмма

```
┌──────────────┐         ┌──────────────┐
│  Category    │         │  Location    │
│──────────────│         │──────────────│
│ id (PK)      │         │ id (PK)      │
│ name         │         │ name         │
│ slug (UK)    │         │ is_active    │
│ is_active    │         │ created_at   │
│ created_at   │         │ updated_at   │
└──────┬───────┘         └──────┬───────┘
       │                        │
       │                        │
       │ FK                     │ FK
       │                        │
┌──────▼───────────────────────────────────────┐
│              Product                         │
│──────────────────────────────────────────────│
│ id (PK)                                      │
│ name                                         │
│ sku (UK)                                     │
│ category_id (FK → Category)                  │
│ is_consumable (Boolean)                      │
│ unit                                         │
│ min_stock                                    │
│ description                                  │
│ created_at / updated_at                      │
└───────┬─────────────────────────┬────────────┘
        │                         │
        │ is_consumable=False     │ is_consumable=True
        │                         │
┌───────▼──────────────┐  ┌───────▼──────────────────┐
│      Asset           │  │       Stock              │
│──────────────────────│  │──────────────────────────│
│ id (PK)              │  │ id (PK)                  │
│ product_id (FK)      │  │ product_id (FK)          │
│ serial_number        │  │ location_id (FK)         │
│ inventory_number(UK) │  │ quantity                 │
│ status               │  │ UK(product, location)    │
│ current_location(FK) │  │ created_at / updated_at  │
│ created_at / updated │  └──────────┬───────────────┘
└──────┬───────────────┘             │
       │                             │
       │                             │
       │ FK                          │ FK
       │                             │
┌──────▼───────────┐    ┌────────────▼──────────────┐
│   Issuance       │    │   StockOperations         │
│──────────────────│    │───────────────────────────│
│ id (PK)          │    │ id (PK)                   │
│ inventory_item   │    │ product_id (FK)           │
│   (FK → Asset)   │    │ operation_type            │
│ recipient        │    │   (receipt/expense/       │
│ issue_date       │    │    transfer)              │
│ return_date      │    │ quantity                  │
│ issue_comment    │    │ from_location_id (FK)     │
│ return_comment   │    │ to_location_id (FK)       │
│ created_at /     │    │ comment                   │
│   updated_at     │    │ timestamp                 │
└──────────────────┘    └───────────────────────────┘

┌─────────────────────────────────────────────┐
│             WriteOff                        │
│─────────────────────────────────────────────│
│ id (PK)                                     │
│ product_id (FK → Product, nullable)         │
│ inventory_item_id (FK → Asset, nullable)    │
│ quantity (для расходников)                  │
│ location_id (FK → Location)                 │
│ reason                                      │
│ date                                        │
│ created_at / updated_at                     │
└─────────────────────────────────────────────┘
```

### Ключевые связи

1. **Product → Asset**: Один товар (техника) может иметь много физических единиц
2. **Product → Stock**: Один товар (расходник) может быть на разных локациях
3. **Product → WriteOff**: Можно списать расходник
4. **Asset → Issuance**: История выдачи техники
5. **Asset → WriteOff**: Можно списать технику
6. **Stock → StockOperations**: История операций со складом

### Статусы техники (Asset)

```
┌──────────────┐      issue       ┌──────────────┐
│  IN_STOCK    │─────────────────>│   ISSUED     │
│ (В наличии)  │<─────────────────│  (Выдана)    │
└──────┬───────┘      return      └──────┬───────┘
       │                                  │
       │ mark_maintenance                 │
       │                                  │
       ▼                                  ▼
┌──────────────┐                 ┌──────────────┐
│ MAINTENANCE  │                 │ WRITTEN_OFF  │
│(Обслуживание)│                 │  (Списана)   │
└──────────────┘                 └──────────────┘
```

---

## Установка и настройка

### Требования

- Python 3.11+
- Redis Server
- PostgreSQL (для production)

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/yourusername/OfficeAssets.git
cd OfficeAssets
```

### Шаг 2: Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
REDIS_URL=redis://127.0.0.1:6379/1
STATIC_ROOT=staticfiles
MEDIA_ROOT=media

# Для production
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Шаг 5: Применение миграций

```bash
python manage.py migrate
```

### Шаг 6: Создание суперпользователя

```bash
python manage.py createsuperuser
```

### Шаг 7: Запуск сервера разработки

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Шаг 8: Запуск Celery (в отдельном терминале)

```bash
# Worker
celery -A settings worker -l info

# Beat (планировщик)
celery -A settings beat -l info
```

### Шаг 9: Запуск Redis (если не запущен)

```bash
redis-server
```

---

## API документация

### Базовый URL

```
http://127.0.0.1:8000/api/v1/
```

### Swagger UI

Интерактивная документация API доступна по адресу:
```
http://127.0.0.1:8000/api/v1/docs/
```

### OpenAPI Schema

```
http://127.0.0.1:8000/api/v1/schema/
```

### Аутентификация

API использует JWT-аутентификацию. Для получения токена:

```bash
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Использование токена в запросах:
```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Основные endpoints

#### Справочники

```bash
# Категории
GET    /api/v1/categories/          # Список категорий
POST   /api/v1/categories/          # Создать категорию
GET    /api/v1/categories/{id}/     # Получить категорию
PUT    /api/v1/categories/{id}/     # Обновить категорию
DELETE /api/v1/categories/{id}/     # Удалить категорию

# Локации
GET    /api/v1/locations/           # Список локаций
POST   /api/v1/locations/           # Создать локацию
GET    /api/v1/locations/{id}/      # Получить локацию
PUT    /api/v1/locations/{id}/      # Обновить локацию
DELETE /api/v1/locations/{id}/      # Удалить локацию
```

#### Товары

```bash
# Товары
GET    /api/v1/products/            # Список товаров
POST   /api/v1/products/            # Создать товар
GET    /api/v1/products/{id}/       # Получить товар
PUT    /api/v1/products/{id}/       # Обновить товар
DELETE /api/v1/products/{id}/       # Удалить товар

# Фильтры
GET    /api/v1/products/consumables/  # Только расходники
GET    /api/v1/products/assets/       # Только техника
```

#### Техника (Assets)

```bash
# Активы
GET    /api/v1/assets/              # Список техники
POST   /api/v1/assets/              # Создать актив
GET    /api/v1/assets/{id}/         # Получить актив
PUT    /api/v1/assets/{id}/         # Обновить актив
DELETE /api/v1/assets/{id}/         # Удалить актив

# Специальные действия
GET    /api/v1/assets/available/    # Доступная техника
GET    /api/v1/assets/issued/       # Выданная техника
POST   /api/v1/assets/{id}/mark_maintenance/  # На обслуживание
```

#### Склад (Stock)

```bash
# Остатки
GET    /api/v1/stock/               # Текущие остатки
GET    /api/v1/stock/low_stock/     # Низкие остатки

# Операции
POST   /api/v1/stock-operation/receipt/    # Приход товара
POST   /api/v1/stock-operation/expense/    # Расход товара
POST   /api/v1/stock-operation/transfer/   # Перемещение товара
GET    /api/v1/stock-operation/            # История операций
GET    /api/v1/stock-operation/{id}/       # Детали операции
```

#### Выдача техники

```bash
# Выдачи
GET    /api/v1/issues/              # История выдач
GET    /api/v1/issues/{id}/         # Детали выдачи
POST   /api/v1/issues/create_issuance/     # Выдать технику
POST   /api/v1/issues/{id}/return_asset/   # Вернуть технику
GET    /api/v1/issues/active/               # Активные выдачи
```

#### Списание

```bash
# Списания
GET    /api/v1/writeoffs/           # История списаний
GET    /api/v1/writeoffs/{id}/      # Детали списания
POST   /api/v1/writeoffs/create_consumable/  # Списать расходник
POST   /api/v1/writeoffs/create_asset/       # Списать технику
```

### Примеры запросов

#### Создание товара (расходника)

```bash
POST /api/v1/products/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Бумага А4",
  "sku": "PAPER-A4-001",
  "category": 1,
  "is_consumable": true,
  "unit": "пачка",
  "min_stock": 10,
  "description": "Бумага для принтера формата А4"
}
```

#### Приход товара на склад

```bash
POST /api/v1/stock-operation/receipt/
Authorization: Bearer <token>
Content-Type: application/json

{
  "product": 1,
  "quantity": 50,
  "to_location": 1,
  "comment": "Поступление от поставщика ООО 'Офис'"
}
```

#### Создание техники

```bash
POST /api/v1/products/
{
  "name": "Ноутбук Dell Latitude",
  "sku": "LAPTOP-DELL-001",
  "category": 2,
  "is_consumable": false,
  "description": "Ноутбук для офисной работы"
}

POST /api/v1/assets/
{
  "product": 1,
  "serial_number": "SN123456789",
  "inventory_number": "INV-2024-001",
  "current_location": 1
}
```

#### Выдача техники сотруднику

```bash
POST /api/v1/issues/create_issuance/
Authorization: Bearer <token>
Content-Type: application/json

{
  "inventory_item": 1,
  "recipient": "Иванов Иван Иванович",
  "issue_comment": "Выдан для работы в отделе продаж"
}
```

#### Возврат техники

```bash
POST /api/v1/issues/{id}/return_asset/
Authorization: Bearer <token>
Content-Type: application/json

{
  "return_comment": "Возвращено в связи с увольнением"
}
```

---

## Бизнес-процессы

### 1. Поступление расходников

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ Поставщик   │─────>│   Приход     │─────>│ Увеличение  │
│ привозит    │      │   товара     │      │  остатков   │
│   товар     │      │   на склад   │      │  на складе  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Создается   │
                     │  запись в    │
                     │ StockOper... │
                     └──────────────┘
```

**API**: `POST /api/v1/stock-operation/receipt/`

### 2. Выдача расходников сотруднику

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ Сотрудник   │─────>│   Расход     │─────>│ Уменьшение  │
│ запрашивает │      │   товара     │      │  остатков   │
│  материалы  │      │   со склада  │      │  на складе  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Создается   │
                     │  запись в    │
                     │ StockOper... │
                     └──────────────┘
```

**API**: `POST /api/v1/stock-operation/expense/`

### 3. Жизненный цикл техники

```
┌──────────────┐
│  Поступление │
│   техники    │
└──────┬───────┘
       │
       ▼
┌──────────────┐      Выдача      ┌──────────────┐
│  На складе   │─────────────────>│    Выдана    │
│  (IN_STOCK)  │<─────────────────│   (ISSUED)   │
└──────┬───────┘      Возврат     └──────────────┘
       │
       │ Неисправность
       ▼
┌──────────────┐      Ремонт      ┌──────────────┐
│ Обслуживание │─────────────────>│  На складе   │
│(MAINTENANCE) │                   │  (IN_STOCK)  │
└──────────────┘                   └──────────────┘
       │
       │ Не подлежит ремонту
       ▼
┌──────────────┐
│   Списана    │
│(WRITTEN_OFF) │
└──────────────┘
```

### 4. Выдача и возврат техники

```
┌─────────────────┐
│  Техника на     │
│  складе         │
│  status=IN_STOCK│
└────────┬────────┘
         │
         │ POST /issues/create_issuance/
         │ {inventory_item, recipient}
         ▼
┌─────────────────┐
│ Создается запись│
│ в Issuance      │
│ issue_date=now  │
└────────┬────────┘
         │
         │ Asset.mark_as_issued()
         ▼
┌─────────────────┐
│  Статус техники │
│  status=ISSUED  │
│  У сотрудника   │
└────────┬────────┘
         │
         │ POST /issues/{id}/return_asset/
         │ {return_comment}
         ▼
┌─────────────────┐
│ Обновляется     │
│ Issuance        │
│ return_date=now │
└────────┬────────┘
         │
         │ Asset.mark_as_returned()
         ▼
┌─────────────────┐
│  Статус техники │
│ status=IN_STOCK │
│  Вернулась      │
└─────────────────┘
```

### 5. Списание

#### Списание расходника:

```
POST /api/v1/writeoffs/create_consumable/
{
  "product": 1,
  "quantity": 5,
  "location": 1,
  "reason": "Истек срок годности"
}

       ▼
┌──────────────────┐
│ WriteOffService  │
│ проверяет остатки│
└────────┬─────────┘
         │
         │ Если достаточно
         ▼
┌──────────────────┐      ┌─────────────────┐
│ Уменьшается      │      │  Создается      │
│ Stock.quantity   │◄─────│  WriteOff       │
│                  │      │  запись         │
└──────────────────┘      └─────────────────┘
```

#### Списание техники:

```
POST /api/v1/writeoffs/create_asset/
{
  "inventory_item": 1,
  "location": 1,
  "reason": "Не подлежит ремонту"
}

       ▼
┌──────────────────┐
│ WriteOffService  │
│ проверяет статус │
└────────┬─────────┘
         │
         │ Если можно списать
         ▼
┌──────────────────┐      ┌─────────────────┐
│ Asset.status =   │      │  Создается      │
│ WRITTEN_OFF      │◄─────│  WriteOff       │
│                  │      │  запись         │
└──────────────────┘      └─────────────────┘
```

---

## Автоматизация

Система использует Celery для автоматизации рутинных задач.

### Настроенные задачи

#### 1. Проверка низких остатков (ежедневно в 9:00)

```python
@shared_task
def check_low_stock():
    """Проверяет товары с низкими остатками"""
    low_stock_items = StockService.get_low_stock_items()
    # Логирование или отправка уведомлений
```

**Расписание**: Каждый день в 9:00 UTC

#### 2. Генерация отчета по списаниям (ежемесячно)

```python
@shared_task
def generate_writeoff_report():
    """Генерирует отчет по списаниям за прошлый месяц"""
    # Сбор данных и формирование отчета
```

**Расписание**: 1-е число каждого месяца в 8:00 UTC

### Конфигурация Celery

```python
# settings/settings.py
CELERY_BEAT_SCHEDULE = {
    'check-low-stock-daily': {
        'task': 'apps.stock.tasks.check_low_stock',
        'schedule': crontab(hour=9, minute=0),
    },
    'monthly-writeoff-report': {
        'task': 'apps.writeoffs.tasks.generate_writeoff_report',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),
    },
}
```

---

## Разработка

### Структура проекта

```
OfficeAssets/
├── apps/                       # Приложения Django
│   ├── references/             # Справочники
│   │   ├── models.py           # Category, Location
│   │   ├── serializers.py      # Сериализаторы
│   │   ├── views.py            # ViewSets
│   │   └── urls.py             # URL маршруты
│   ├── products/               # Товары
│   │   ├── models.py           # Product
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── assets/                 # Техника
│   │   ├── models.py           # Asset
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── stock/                  # Склад
│   │   ├── models.py           # Stock, StockOperations
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # StockService
│   │   ├── tasks.py            # Celery задачи
│   │   └── urls.py
│   ├── issues/                 # Выдача
│   │   ├── models.py           # Issuance
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # IssuancesService
│   │   └── urls.py
│   ├── writeoffs/              # Списание
│   │   ├── models.py           # WriteOff
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py         # WriteOffService
│   │   ├── tasks.py            # Celery задачи
│   │   └── urls.py
│   └── core/                   # Ядро
│       ├── exceptions.py       # Кастомные исключения
│       └── models.py           # Базовые модели
├── settings/                   # Настройки проекта
│   ├── settings.py             # Основные настройки
│   ├── urls.py                 # Корневые URL
│   ├── wsgi.py                 # WSGI конфигурация
│   └── celery.py               # Celery конфигурация
├── logs/                       # Логи приложения
├── media/                      # Загруженные файлы
├── staticfiles/                # Статические файлы
├── requirements.txt            # Зависимости Python
├── manage.py                   # Django управление
└── db.sqlite3                  # База данных (dev)
```

### Запуск тестов

```bash
# Установка pytest (если не установлен)
pip install pytest pytest-django

# Запуск тестов
pytest

# С покрытием кода
pytest --cov=apps --cov-report=html
```

### Создание миграций

```bash
# Создать миграции для всех приложений
python manage.py makemigrations

# Создать миграции для конкретного приложения
python manage.py makemigrations products

# Применить миграции
python manage.py migrate
```

### Запуск линтеров

```bash
# Установка инструментов
pip install flake8 black isort

# Форматирование кода
black .
isort .

# Проверка стиля
flake8 apps/
```

### Архитектурные принципы

1. **Service Layer Pattern**: Вся бизнес-логика в сервисах (`services.py`)
2. **Immutable History**: История операций не может быть изменена
3. **Transaction Safety**: Критические операции выполняются в транзакциях
4. **Validation**: Валидация на уровне моделей через `clean()` и `full_clean()`
5. **Query Optimization**: Использование `select_related()` и `prefetch_related()`

### Добавление нового функционала

1. Создайте модели в `models.py`
2. Создайте сериализаторы в `serializers.py`
3. Реализуйте бизнес-логику в `services.py`
4. Создайте ViewSets в `views.py`
5. Зарегистрируйте URL в `urls.py`
6. Создайте и примените миграции

---

## Production deployment

### Настройка для production

1. Создайте `.env` файл с production настройками:

```env
SECRET_KEY=super-secret-production-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/officeassets
REDIS_URL=redis://127.0.0.1:6379/1
```

2. Соберите статические файлы:

```bash
python manage.py collectstatic --noinput
```

3. Настройте PostgreSQL базу данных

4. Запустите с Gunicorn:

```bash
gunicorn settings.wsgi:application --bind 0.0.0.0:8000
```

5. Настройте Nginx как reverse proxy

6. Запустите Celery worker и beat:

```bash
celery -A settings worker -l info
celery -A settings beat -l info
```

### Docker (опционально)

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "settings.wsgi:application", "--bind", "0.0.0.0:8000"]
```

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: officeassets
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn settings.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A settings worker -l info
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A settings beat -l info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## Дополнительная документация

Полная документация проекта доступна в директории [docs/](docs/):

### 📘 Для разработчиков
- **[API Guide](docs/API_GUIDE.md)** - Подробное руководство по всем API endpoints с примерами запросов
- **[Architecture](docs/ARCHITECTURE.md)** - Архитектура системы, паттерны проектирования, потоки данных
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - Полная схема базы данных с ER-диаграммами и описанием таблиц
- **[Examples](docs/EXAMPLES.md)** - Практические примеры использования API (curl, Python, JavaScript)

### 🚀 Для DevOps
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Пошаговое руководство по развертыванию (локально, production, Docker)

### 📊 Диаграммы и схемы

В документации вы найдете:
- ER-диаграммы базы данных
- Диаграммы потоков данных
- Схемы бизнес-процессов
- Архитектурные диаграммы

---

## Поддержка

### Нашли баг или хотите предложить улучшение?

- **Проверьте существующие [Issues](https://github.com/yourusername/OfficeAssets/issues)**
- **Создайте новый Issue** с подробным описанием проблемы
- **Или отправьте Pull Request** с вашими исправлениями

### Полезные ссылки

Если проект оказался полезным:
- ⭐ Поставьте звезду на GitHub
- 📢 Расскажите о проекте коллегам
- 💡 Поделитесь идеями по улучшению
- 🐛 Сообщайте о найденных багах

---

## Лицензия

Проект распространяется под лицензией MIT License. Подробности в файле [LICENSE](LICENSE).

---

## Авторы и благодарности

Проект разработан с использованием:
- [Django](https://www.djangoproject.com/) - веб-фреймворк
- [Django REST Framework](https://www.django-rest-framework.org/) - toolkit для построения API
- [Celery](https://docs.celeryproject.org/) - асинхронная обработка задач
- [PostgreSQL](https://www.postgresql.org/) - база данных
- [Redis](https://redis.io/) - кэш и брокер сообщений

---

## Changelog

### Версия 1.0.0 (2024)

**Основной функционал:**
- ✅ Управление техникой с инвентарными номерами
- ✅ Количественный учет расходных материалов
- ✅ Операции прихода, расхода и перемещения
- ✅ Выдача и возврат техники сотрудникам
- ✅ Списание техники и расходников

**API:**
- ✅ REST API для всех операций
- ✅ JWT аутентификация
- ✅ OpenAPI 3.0 документация (Swagger UI)
- ✅ Фильтрация, поиск и пагинация

**Автоматизация:**
- ✅ Celery для фоновых задач
- ✅ Автоматическая проверка низких остатков
- ✅ Ежемесячная генерация отчетов

**Развертывание:**
- ✅ Docker support
- ✅ Production-ready конфигурация
- ✅ Comprehensive документация

---

## Roadmap

### Версия 1.1 (планируется)
- [ ] WebSocket для real-time уведомлений
- [ ] Экспорт отчетов в Excel/PDF
- [ ] QR-коды для техники
- [ ] Расширенная аналитика и дашборды

### Версия 2.0 (будущее)
- [ ] Мобильное приложение (iOS/Android)
- [ ] Интеграция с 1C
- [ ] Role-based access control (RBAC)
- [ ] Многопользовательский режим с правами доступа
- [ ] История изменений (Audit log)

---

## Контакты

- **GitHub**: [https://github.com/yourusername/OfficeAssets](https://github.com/yourusername/OfficeAssets)
- **Issues**: [https://github.com/yourusername/OfficeAssets/issues](https://github.com/yourusername/OfficeAssets/issues)

---

**Сделано с ❤️ для упрощения учета офисного имущества**
