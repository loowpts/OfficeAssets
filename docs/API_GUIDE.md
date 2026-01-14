# Руководство по API OfficeAssets

## Содержание
- [Аутентификация](#аутентификация)
- [Общие принципы](#общие-принципы)
- [Endpoints по модулям](#endpoints-по-модулям)
- [Примеры использования](#примеры-использования)
- [Коды ответов](#коды-ответов)
- [Обработка ошибок](#обработка-ошибок)

---

## Аутентификация

### Получение JWT токена

```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Ответ:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Обновление токена

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Ответ:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Использование токена

Все запросы к API требуют заголовок авторизации:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## Общие принципы

### Пагинация

Все списковые endpoints поддерживают пагинацию (20 элементов на страницу):

```http
GET /api/v1/products/?page=2
```

**Ответ:**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/products/?page=3",
  "previous": "http://localhost:8000/api/v1/products/?page=1",
  "results": [...]
}
```

### Фильтрация

```http
# Фильтрация по полям
GET /api/v1/assets/?status=in_stock&current_location=1

# Поиск
GET /api/v1/products/?search=ноутбук

# Сортировка
GET /api/v1/assets/?ordering=-created_at
GET /api/v1/assets/?ordering=inventory_number
```

### Форматы данных

**Даты**: ISO 8601 формат
```json
{
  "created_at": "2024-01-15T10:30:00Z",
  "issue_date": "2024-01-15"
}
```

**Количество**: Decimal
```json
{
  "quantity": "10.50"
}
```

---

## Endpoints по модулям

## 1. Справочники (References)

### Категории

#### Список категорий
```http
GET /api/v1/categories/
```

**Параметры:**
- `is_active` - фильтр по активности (true/false)
- `search` - поиск по названию
- `ordering` - сортировка (name, -created_at)

**Ответ:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Компьютеры",
      "slug": "computers",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Создание категории
```http
POST /api/v1/categories/
Content-Type: application/json

{
  "name": "Оргтехника",
  "is_active": true
}
```

**Ответ:** `201 Created`
```json
{
  "id": 2,
  "name": "Оргтехника",
  "slug": "orgtechnika",
  "is_active": true,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

#### Обновление категории
```http
PUT /api/v1/categories/2/
Content-Type: application/json

{
  "name": "Офисная техника",
  "is_active": true
}
```

#### Удаление категории
```http
DELETE /api/v1/categories/2/
```

### Локации

#### Список локаций
```http
GET /api/v1/locations/
```

**Ответ:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Главный склад",
      "is_active": true,
      "created_at": "2024-01-10T09:00:00Z",
      "updated_at": "2024-01-10T09:00:00Z"
    },
    {
      "id": 2,
      "name": "Офис - 2 этаж",
      "is_active": true,
      "created_at": "2024-01-10T09:05:00Z",
      "updated_at": "2024-01-10T09:05:00Z"
    }
  ]
}
```

---

## 2. Товары (Products)

### Список товаров
```http
GET /api/v1/products/
```

**Параметры:**
- `category` - фильтр по категории
- `is_consumable` - фильтр по типу (true - расходник, false - техника)
- `search` - поиск по названию или SKU
- `ordering` - сортировка

**Ответ:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "Бумага А4",
      "sku": "PAPER-A4-001",
      "category": {
        "id": 3,
        "name": "Канцелярия"
      },
      "is_consumable": true,
      "unit": "пачка",
      "min_stock": "10.00",
      "description": "Бумага для принтера",
      "created_at": "2024-01-12T14:00:00Z",
      "updated_at": "2024-01-12T14:00:00Z"
    }
  ]
}
```

### Только расходники
```http
GET /api/v1/products/consumables/
```

### Только техника
```http
GET /api/v1/products/assets/
```

### Создание товара
```http
POST /api/v1/products/
Content-Type: application/json

{
  "name": "Ноутбук Dell Latitude 5420",
  "sku": "LAPTOP-DELL-5420",
  "category": 1,
  "is_consumable": false,
  "description": "Ноутбук для офисной работы, Intel i5, 16GB RAM"
}
```

**Ответ:** `201 Created`

---

## 3. Техника (Assets)

### Список техники
```http
GET /api/v1/assets/
```

**Параметры:**
- `product` - фильтр по товару
- `status` - фильтр по статусу (in_stock, issued, maintenance, written_off)
- `current_location` - фильтр по локации
- `search` - поиск по инвентарному/серийному номеру

**Ответ:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Ноутбук Dell Latitude 5420",
        "sku": "LAPTOP-DELL-5420"
      },
      "serial_number": "DELL-SN-123456789",
      "inventory_number": "INV-2024-001",
      "status": "in_stock",
      "current_location": {
        "id": 1,
        "name": "Главный склад"
      },
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Доступная техника
```http
GET /api/v1/assets/available/
```

Возвращает только технику со статусом `in_stock`.

### Выданная техника
```http
GET /api/v1/assets/issued/
```

Возвращает только технику со статусом `issued`.

### Создание актива
```http
POST /api/v1/assets/
Content-Type: application/json

{
  "product": 1,
  "serial_number": "DELL-SN-987654321",
  "inventory_number": "INV-2024-002",
  "current_location": 1
}
```

**Ответ:** `201 Created`

### Отправить на обслуживание
```http
POST /api/v1/assets/1/mark_maintenance/
```

Меняет статус на `maintenance`.

**Ответ:** `200 OK`
```json
{
  "id": 1,
  "status": "maintenance",
  "message": "Asset marked as under maintenance"
}
```

---

## 4. Склад (Stock)

### Текущие остатки
```http
GET /api/v1/stock/
```

**Параметры:**
- `product` - фильтр по товару
- `location` - фильтр по локации

**Ответ:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Бумага А4",
        "sku": "PAPER-A4-001",
        "unit": "пачка",
        "min_stock": "10.00"
      },
      "location": {
        "id": 1,
        "name": "Главный склад"
      },
      "quantity": "45.00",
      "is_low_stock": false,
      "created_at": "2024-01-12T14:30:00Z",
      "updated_at": "2024-01-15T09:20:00Z"
    }
  ]
}
```

### Низкие остатки
```http
GET /api/v1/stock/low_stock/
```

Возвращает товары, где `quantity <= min_stock`.

### Приход товара
```http
POST /api/v1/stock-operation/receipt/
Content-Type: application/json

{
  "product": 1,
  "quantity": "50.00",
  "to_location": 1,
  "comment": "Поступление от поставщика ООО 'Офис Снаб'"
}
```

**Ответ:** `201 Created`
```json
{
  "id": 1,
  "product": {
    "id": 1,
    "name": "Бумага А4"
  },
  "operation_type": "receipt",
  "quantity": "50.00",
  "from_location": null,
  "to_location": {
    "id": 1,
    "name": "Главный склад"
  },
  "comment": "Поступление от поставщика ООО 'Офис Снаб'",
  "timestamp": "2024-01-15T14:00:00Z"
}
```

**Что происходит:**
1. Создается запись в `StockOperations`
2. Увеличивается `Stock.quantity` для товара на локации
3. Если записи Stock нет, она создается

### Расход товара
```http
POST /api/v1/stock-operation/expense/
Content-Type: application/json

{
  "product": 1,
  "quantity": "5.00",
  "from_location": 1,
  "comment": "Выдано сотруднику Иванову И.И."
}
```

**Ответ:** `201 Created`

**Что происходит:**
1. Проверяется наличие достаточного количества
2. Уменьшается `Stock.quantity`
3. Создается запись в `StockOperations`

**Ошибка при недостаточном количестве:**
```json
{
  "error": "Insufficient stock",
  "detail": "Not enough quantity for this operation"
}
```

### Перемещение товара
```http
POST /api/v1/stock-operation/transfer/
Content-Type: application/json

{
  "product": 1,
  "quantity": "10.00",
  "from_location": 1,
  "to_location": 2,
  "comment": "Перемещение в офис на 2 этаж"
}
```

**Ответ:** `201 Created`

**Что происходит:**
1. Проверяется наличие на `from_location`
2. Уменьшается количество на `from_location`
3. Увеличивается количество на `to_location`
4. Создается запись в `StockOperations`

### История операций
```http
GET /api/v1/stock-operation/
```

**Параметры:**
- `product` - фильтр по товару
- `operation_type` - фильтр по типу (receipt, expense, transfer)
- `from_location` - фильтр по исходной локации
- `to_location` - фильтр по целевой локации
- `ordering` - сортировка (по умолчанию -timestamp)

**Ответ:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 3,
      "product": {
        "id": 1,
        "name": "Бумага А4"
      },
      "operation_type": "expense",
      "quantity": "5.00",
      "from_location": {
        "id": 1,
        "name": "Главный склад"
      },
      "to_location": null,
      "comment": "Выдано сотруднику",
      "timestamp": "2024-01-15T14:30:00Z"
    }
  ]
}
```

---

## 5. Выдача техники (Issues)

### История выдач
```http
GET /api/v1/issues/
```

**Параметры:**
- `inventory_item` - фильтр по активу
- `recipient` - поиск по получателю
- `ordering` - сортировка

**Ответ:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "inventory_item": {
        "id": 1,
        "inventory_number": "INV-2024-001",
        "product": {
          "name": "Ноутбук Dell Latitude 5420"
        }
      },
      "recipient": "Иванов Иван Иванович",
      "issue_date": "2024-01-10",
      "return_date": null,
      "issue_comment": "Выдан для работы в отделе продаж",
      "return_comment": null,
      "is_active": true,
      "created_at": "2024-01-10T09:00:00Z",
      "updated_at": "2024-01-10T09:00:00Z"
    }
  ]
}
```

### Активные выдачи
```http
GET /api/v1/issues/active/
```

Возвращает выдачи, где `return_date` равен `null`.

### Выдать технику
```http
POST /api/v1/issues/create_issuance/
Content-Type: application/json

{
  "inventory_item": 1,
  "recipient": "Петров Петр Петрович",
  "issue_comment": "Выдан для работы из дома"
}
```

**Ответ:** `201 Created`
```json
{
  "id": 2,
  "inventory_item": {
    "id": 1,
    "inventory_number": "INV-2024-001",
    "status": "issued"
  },
  "recipient": "Петров Петр Петрович",
  "issue_date": "2024-01-15",
  "return_date": null,
  "issue_comment": "Выдан для работы из дома",
  "return_comment": null,
  "is_active": true
}
```

**Что происходит:**
1. Проверяется, что техника доступна (status=in_stock)
2. Создается запись в `Issuance`
3. Статус техники меняется на `issued`

**Ошибки:**
```json
// Если техника уже выдана
{
  "error": "Asset is not available",
  "detail": "This asset is already issued or not in stock"
}
```

### Вернуть технику
```http
POST /api/v1/issues/1/return_asset/
Content-Type: application/json

{
  "return_comment": "Возврат в связи с окончанием проекта"
}
```

**Ответ:** `200 OK`
```json
{
  "id": 1,
  "inventory_item": {
    "id": 1,
    "status": "in_stock"
  },
  "recipient": "Иванов Иван Иванович",
  "issue_date": "2024-01-10",
  "return_date": "2024-01-15",
  "return_comment": "Возврат в связи с окончанием проекта",
  "is_active": false
}
```

**Что происходит:**
1. Устанавливается `return_date` (текущая дата)
2. Записывается `return_comment`
3. Статус техники меняется на `in_stock`

---

## 6. Списание (WriteOffs)

### История списаний
```http
GET /api/v1/writeoffs/
```

**Параметры:**
- `product` - фильтр по товару (для расходников)
- `inventory_item` - фильтр по активу (для техники)
- `location` - фильтр по локации
- `date` - фильтр по дате списания

**Ответ:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Бумага А4"
      },
      "inventory_item": null,
      "quantity": "5.00",
      "location": {
        "id": 1,
        "name": "Главный склад"
      },
      "reason": "Истек срок годности",
      "date": "2024-01-15",
      "created_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "product": null,
      "inventory_item": {
        "id": 5,
        "inventory_number": "INV-2023-050",
        "product": {
          "name": "Ноутбук Dell Latitude"
        }
      },
      "quantity": null,
      "location": {
        "id": 1,
        "name": "Главный склад"
      },
      "reason": "Неисправен, не подлежит ремонту",
      "date": "2024-01-14",
      "created_at": "2024-01-14T11:00:00Z"
    }
  ]
}
```

### Списать расходник
```http
POST /api/v1/writeoffs/create_consumable/
Content-Type: application/json

{
  "product": 1,
  "quantity": "3.00",
  "location": 1,
  "reason": "Бракованная партия"
}
```

**Ответ:** `201 Created`

**Что происходит:**
1. Проверяется наличие достаточного количества на складе
2. Уменьшается `Stock.quantity`
3. Создается запись в `WriteOff`

### Списать технику
```http
POST /api/v1/writeoffs/create_asset/
Content-Type: application/json

{
  "inventory_item": 5,
  "location": 1,
  "reason": "Неисправен, экономически нецелесообразно ремонтировать"
}
```

**Ответ:** `201 Created`

**Что происходит:**
1. Проверяется, что техника не выдана (status != issued)
2. Статус техники меняется на `written_off`
3. Создается запись в `WriteOff`

**Ошибки:**
```json
// Если техника сейчас выдана
{
  "error": "Cannot write off issued asset",
  "detail": "Asset must be returned before write-off"
}
```

---

## Коды ответов

| Код | Описание |
|-----|----------|
| 200 | OK - Успешный запрос |
| 201 | Created - Ресурс создан |
| 204 | No Content - Успешное удаление |
| 400 | Bad Request - Неверные данные |
| 401 | Unauthorized - Требуется аутентификация |
| 403 | Forbidden - Недостаточно прав |
| 404 | Not Found - Ресурс не найден |
| 500 | Internal Server Error - Ошибка сервера |

---

## Обработка ошибок

### Ошибки валидации (400)
```json
{
  "field_name": [
    "This field is required.",
    "This field may not be blank."
  ]
}
```

### Бизнес-логика ошибки (400)
```json
{
  "error": "Insufficient stock",
  "detail": "Not enough quantity in location 'Main warehouse' for product 'Paper A4'"
}
```

### Ошибка аутентификации (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Ресурс не найден (404)
```json
{
  "detail": "Not found."
}
```

---

## Полезные комбинации запросов

### Сценарий 1: Поступление новой партии техники

```bash
# 1. Создать товар (если еще нет)
POST /api/v1/products/
{
  "name": "Монитор LG 24\"",
  "sku": "MONITOR-LG-24",
  "category": 1,
  "is_consumable": false
}

# 2. Создать 10 единиц техники
for i in 1..10:
  POST /api/v1/assets/
  {
    "product": 2,
    "serial_number": "LG-SN-{i}",
    "inventory_number": "INV-2024-{100+i}",
    "current_location": 1
  }
```

### Сценарий 2: Выдача техники новому сотруднику

```bash
# 1. Найти доступную технику
GET /api/v1/assets/available/?product=1

# 2. Выдать найденную технику
POST /api/v1/issues/create_issuance/
{
  "inventory_item": 1,
  "recipient": "Сидоров Сидор Сидорович",
  "issue_comment": "Выдан новому сотруднику отдела IT"
}

# 3. Проверить статус техники
GET /api/v1/assets/1/
# status теперь "issued"
```

### Сценарий 3: Инвентаризация расходников

```bash
# 1. Получить все остатки
GET /api/v1/stock/

# 2. Проверить низкие остатки
GET /api/v1/stock/low_stock/

# 3. Заказать товары с низкими остатками
POST /api/v1/stock-operation/receipt/
{
  "product": 1,
  "quantity": "100.00",
  "to_location": 1,
  "comment": "Закуп по результатам инвентаризации"
}
```

### Сценарий 4: Списание старой техники

```bash
# 1. Найти выданную технику
GET /api/v1/assets/issued/

# 2. Вернуть технику
POST /api/v1/issues/5/return_asset/
{
  "return_comment": "Возвращен для списания (устарел)"
}

# 3. Списать технику
POST /api/v1/writeoffs/create_asset/
{
  "inventory_item": 10,
  "location": 1,
  "reason": "Моральное устаревание, нецелесообразно использовать"
}

# 4. Проверить статус
GET /api/v1/assets/10/
# status теперь "written_off"
```

---

## Rate Limiting

В текущей версии rate limiting не настроен. Рекомендуется настроить его в production окружении.

Рекомендуемые лимиты:
- Аутентификация: 5 запросов в минуту
- Чтение (GET): 100 запросов в минуту
- Запись (POST/PUT/DELETE): 50 запросов в минуту

---

## WebSocket / Real-time обновления

В текущей версии не реализовано. Для real-time обновлений рекомендуется:
- Использовать Django Channels
- Настроить WebSocket подключения
- Отправлять события при изменении данных

---

## Экспорт данных

Для экспорта данных можно использовать:

```bash
# CSV экспорт (требует настройки)
GET /api/v1/assets/?format=csv

# JSON экспорт (по умолчанию)
GET /api/v1/assets/

# Excel экспорт (требует дополнительной настройки)
GET /api/v1/assets/?format=xlsx
```

---

## Версионирование API

Текущая версия: **v1**

При изменении API создается новая версия:
- `/api/v1/` - текущая версия
- `/api/v2/` - будущая версия (breaking changes)

Обратная совместимость поддерживается минимум 6 месяцев после выхода новой версии.
