# OfficeAssets - Быстрый старт

## Установка за 5 минут

### 1. Клонирование и подготовка

```bash
git clone https://github.com/yourusername/OfficeAssets.git
cd OfficeAssets
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
REDIS_URL=redis://127.0.0.1:6379/1
```

### 3. База данных

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Запуск

```bash
# Терминал 1: Django
python manage.py runserver

# Терминал 2: Celery Worker
celery -A settings worker -l info

# Терминал 3: Celery Beat
celery -A settings beat -l info
```

### 5. Готово!

- **Приложение**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/api/v1/docs/
- **Admin**: http://127.0.0.1:8000/admin

---

## Первые шаги

### 1. Получите JWT токен

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

Сохраните `access` токен.

### 2. Создайте категорию

```bash
export TOKEN="your_access_token"

curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Компьютерная техника", "is_active": true}'
```

### 3. Создайте локацию

```bash
curl -X POST http://localhost:8000/api/v1/locations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Главный склад", "is_active": true}'
```

### 4. Добавьте товар

```bash
# Расходник
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Бумага А4",
    "sku": "PAPER-A4-001",
    "category": 1,
    "is_consumable": true,
    "unit": "пачка",
    "min_stock": 10
  }'

# Техника
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ноутбук Dell",
    "sku": "LAPTOP-DELL-001",
    "category": 1,
    "is_consumable": false
  }'
```

### 5. Операции

```bash
# Приход расходника
curl -X POST http://localhost:8000/api/v1/stock-operation/receipt/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "quantity": 100,
    "to_location": 1,
    "comment": "Первая поставка"
  }'

# Создание актива (техники)
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 2,
    "serial_number": "DELL-SN-123",
    "inventory_number": "INV-2024-001",
    "current_location": 1
  }'

# Выдача техники
curl -X POST http://localhost:8000/api/v1/issues/create_issuance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 1,
    "recipient": "Иванов И.И.",
    "issue_comment": "Выдан для работы"
  }'
```

---

## Основные команды

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver

# Собрать статику
python manage.py collectstatic

# Celery Worker
celery -A settings worker -l info

# Celery Beat
celery -A settings beat -l info

# Тесты
pytest
pytest --cov=apps
```

---

## Основные URL

| Описание | URL |
|----------|-----|
| API Docs (Swagger) | http://localhost:8000/api/v1/docs/ |
| API Schema | http://localhost:8000/api/v1/schema/ |
| Admin Panel | http://localhost:8000/admin/ |
| Категории | http://localhost:8000/api/v1/categories/ |
| Локации | http://localhost:8000/api/v1/locations/ |
| Товары | http://localhost:8000/api/v1/products/ |
| Техника | http://localhost:8000/api/v1/assets/ |
| Остатки | http://localhost:8000/api/v1/stock/ |
| Операции | http://localhost:8000/api/v1/stock-operation/ |
| Выдачи | http://localhost:8000/api/v1/issues/ |
| Списания | http://localhost:8000/api/v1/writeoffs/ |

---

## Структура проекта

```
OfficeAssets/
├── apps/                   # Django приложения
│   ├── references/         # Справочники (Category, Location)
│   ├── products/           # Товары (Product)
│   ├── assets/             # Техника (Asset)
│   ├── stock/              # Остатки (Stock, StockOperations)
│   ├── issues/             # Выдачи (Issuance)
│   ├── writeoffs/          # Списания (WriteOff)
│   └── core/               # Общие компоненты
├── settings/               # Настройки Django
├── docs/                   # Документация
├── logs/                   # Логи
├── media/                  # Загруженные файлы
├── staticfiles/            # Статические файлы
├── requirements.txt        # Python зависимости
├── manage.py               # Django CLI
└── README.md               # Основная документация
```

---

## Основные модели

```python
# Справочники
Category        # Категории товаров
Location        # Локации (склады, офисы)

# Товары
Product         # Каталог товаров (техника и расходники)

# Учет техники
Asset           # Физические единицы техники с инвентарными номерами

# Учет расходников
Stock           # Количественные остатки расходников
StockOperations # История операций (приход, расход, перемещение)

# Выдача
Issuance        # Выдача и возврат техники

# Списание
WriteOff        # Списание техники и расходников
```

---

## Типичные сценарии

### Сценарий 1: Поступление расходников

1. Создать товар (Product) с `is_consumable=True`
2. Создать операцию прихода (StockOperations - receipt)
3. Система автоматически обновит Stock

### Сценарий 2: Учет новой техники

1. Создать товар (Product) с `is_consumable=False`
2. Создать активы (Asset) для каждой единицы техники
3. Указать инвентарный номер и локацию

### Сценарий 3: Выдача техники сотруднику

1. Найти доступную технику (Asset со статусом `in_stock`)
2. Создать выдачу (Issuance)
3. Система автоматически изменит статус на `issued`

### Сценарий 4: Возврат техники

1. Найти активную выдачу (Issuance где `return_date=null`)
2. Вызвать endpoint `return_asset`
3. Система установит `return_date` и вернет статус в `in_stock`

### Сценарий 5: Списание

**Расходник:**
1. Вызвать endpoint `writeoffs/create_consumable/`
2. Указать товар, количество, локацию и причину
3. Система уменьшит Stock

**Техника:**
1. Вызвать endpoint `writeoffs/create_asset/`
2. Указать актив, локацию и причину
3. Система изменит статус на `written_off`

---

## Полезные фильтры

```bash
# Товары
?category=1                 # По категории
?is_consumable=true         # Только расходники
?search=ноутбук             # Поиск по названию/SKU

# Техника
?status=in_stock            # По статусу
?current_location=1         # По локации
?search=INV-2024-001        # Поиск по инв. номеру

# Остатки
?product=1                  # Конкретный товар
?location=1                 # Конкретная локация

# Операции
?operation_type=receipt     # По типу операции
?product=1                  # По товару
?ordering=-timestamp        # Сортировка

# Выдачи
?recipient=Иванов           # Поиск по получателю
?inventory_item=1           # По активу

# Список всех фильтров в Swagger UI
```

---

## Troubleshooting

### Ошибка: "ConnectionRefusedError: [Errno 61] Connection refused"
**Решение:** Запустите Redis
```bash
# macOS
brew services start redis

# Ubuntu
sudo systemctl start redis-server
```

### Ошибка: "django.db.utils.OperationalError: FATAL: database does not exist"
**Решение:** Создайте базу данных или запустите миграции
```bash
python manage.py migrate
```

### Ошибка: "Asset is not available"
**Решение:** Проверьте статус техники - можно выдать только технику со статусом `in_stock`

### Ошибка: "Insufficient stock"
**Решение:** На складе недостаточно товара для операции расхода

---

## Что дальше?

### 📚 Изучить документацию
- [API Guide](docs/API_GUIDE.md) - все endpoints с примерами
- [Architecture](docs/ARCHITECTURE.md) - как устроена система
- [Examples](docs/EXAMPLES.md) - практические примеры

### 🚀 Развернуть в production
- [Deployment Guide](docs/DEPLOYMENT.md) - пошаговое руководство

### 🤝 Внести вклад
- [Contributing](CONTRIBUTING.md) - как участвовать в разработке

---

## Поддержка

- **Документация**: [docs/](docs/)
- **Issues**: https://github.com/yourusername/OfficeAssets/issues
- **API Docs**: http://localhost:8000/api/v1/docs/

---

**Приятного использования OfficeAssets! 🎉**
