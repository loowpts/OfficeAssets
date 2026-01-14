# Примеры использования API OfficeAssets

## Содержание
- [Базовые сценарии](#базовые-сценарии)
- [Управление справочниками](#управление-справочниками)
- [Работа с товарами](#работа-с-товарами)
- [Учет техники](#учет-техники)
- [Складские операции](#складские-операции)
- [Выдача и возврат](#выдача-и-возврат)
- [Списание](#списание)
- [Комплексные сценарии](#комплексные-сценарии)

---

## Базовые сценарии

### Получение JWT токена

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

**Ответ:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Использование токена в запросах

```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X GET http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Управление справочниками

### Создание категорий

```bash
# Создать категорию "Компьютерная техника"
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Компьютерная техника",
    "is_active": true
  }'

# Создать категорию "Канцелярия"
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Канцелярия",
    "is_active": true
  }'
```

### Создание локаций

```bash
# Главный склад
curl -X POST http://localhost:8000/api/v1/locations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Главный склад",
    "is_active": true
  }'

# Офис - 2 этаж
curl -X POST http://localhost:8000/api/v1/locations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Офис - 2 этаж",
    "is_active": true
  }'

# Офис - 3 этаж
curl -X POST http://localhost:8000/api/v1/locations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Офис - 3 этаж",
    "is_active": true
  }'
```

### Получение всех категорий

```bash
curl -X GET http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Работа с товарами

### Создание товара (техника)

```bash
# Ноутбук
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ноутбук Dell Latitude 5420",
    "sku": "LAPTOP-DELL-5420",
    "category": 1,
    "is_consumable": false,
    "description": "Ноутбук для офисной работы. Intel Core i5-11500, 16GB RAM, 512GB SSD"
  }'

# Монитор
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Монитор LG 24\" Full HD",
    "sku": "MONITOR-LG-24",
    "category": 1,
    "is_consumable": false,
    "description": "Монитор 24 дюйма, разрешение 1920x1080"
  }'
```

### Создание товара (расходник)

```bash
# Бумага А4
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Бумага А4 белая",
    "sku": "PAPER-A4-WHITE",
    "category": 2,
    "is_consumable": true,
    "unit": "пачка",
    "min_stock": 10,
    "description": "Бумага для принтера формата А4, 500 листов в пачке"
  }'

# Ручки
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ручка шариковая синяя",
    "sku": "PEN-BLUE",
    "category": 2,
    "is_consumable": true,
    "unit": "шт",
    "min_stock": 50,
    "description": "Ручка шариковая, синяя паста"
  }'

# Картриджи для принтера
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Картридж HP 305A черный",
    "sku": "CARTRIDGE-HP-305A-BLACK",
    "category": 1,
    "is_consumable": true,
    "unit": "шт",
    "min_stock": 3,
    "description": "Картридж для принтера HP LaserJet Pro"
  }'
```

### Поиск товаров

```bash
# Поиск по названию
curl -X GET "http://localhost:8000/api/v1/products/?search=ноутбук" \
  -H "Authorization: Bearer $TOKEN"

# Получить только расходники
curl -X GET "http://localhost:8000/api/v1/products/consumables/" \
  -H "Authorization: Bearer $TOKEN"

# Получить только технику
curl -X GET "http://localhost:8000/api/v1/products/assets/" \
  -H "Authorization: Bearer $TOKEN"

# Фильтр по категории
curl -X GET "http://localhost:8000/api/v1/products/?category=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Учет техники

### Создание активов (единиц техники)

```bash
# Ноутбук #1
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "serial_number": "DELL-SN-123456789",
    "inventory_number": "INV-2024-001",
    "current_location": 1
  }'

# Ноутбук #2
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "serial_number": "DELL-SN-987654321",
    "inventory_number": "INV-2024-002",
    "current_location": 1
  }'

# Монитор #1
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 2,
    "serial_number": "LG-SN-111222333",
    "inventory_number": "INV-2024-003",
    "current_location": 1
  }'
```

### Получение списка техники

```bash
# Вся техника
curl -X GET http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN"

# Только доступная техника
curl -X GET http://localhost:8000/api/v1/assets/available/ \
  -H "Authorization: Bearer $TOKEN"

# Только выданная техника
curl -X GET http://localhost:8000/api/v1/assets/issued/ \
  -H "Authorization: Bearer $TOKEN"

# Фильтр по статусу
curl -X GET "http://localhost:8000/api/v1/assets/?status=in_stock" \
  -H "Authorization: Bearer $TOKEN"

# Фильтр по локации
curl -X GET "http://localhost:8000/api/v1/assets/?current_location=1" \
  -H "Authorization: Bearer $TOKEN"

# Поиск по инвентарному номеру
curl -X GET "http://localhost:8000/api/v1/assets/?search=INV-2024-001" \
  -H "Authorization: Bearer $TOKEN"
```

### Отправка техники на обслуживание

```bash
curl -X POST http://localhost:8000/api/v1/assets/1/mark_maintenance/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Складские операции

### Приход товара на склад

```bash
# Приход бумаги А4
curl -X POST http://localhost:8000/api/v1/stock-operation/receipt/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 3,
    "quantity": 100,
    "to_location": 1,
    "comment": "Поступление от поставщика ООО Офис Снаб"
  }'

# Приход ручек
curl -X POST http://localhost:8000/api/v1/stock-operation/receipt/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 4,
    "quantity": 200,
    "to_location": 1,
    "comment": "Закупка канцелярских товаров"
  }'

# Приход картриджей
curl -X POST http://localhost:8000/api/v1/stock-operation/receipt/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 5,
    "quantity": 10,
    "to_location": 1,
    "comment": "Закупка расходников для принтеров"
  }'
```

### Расход товара со склада

```bash
# Выдача бумаги
curl -X POST http://localhost:8000/api/v1/stock-operation/expense/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 3,
    "quantity": 10,
    "from_location": 1,
    "comment": "Выдано для офиса на 2 этаже"
  }'

# Выдача ручек
curl -X POST http://localhost:8000/api/v1/stock-operation/expense/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 4,
    "quantity": 20,
    "from_location": 1,
    "comment": "Выдано сотрудникам отдела продаж"
  }'
```

### Перемещение товара между локациями

```bash
# Перемещение бумаги на 2 этаж
curl -X POST http://localhost:8000/api/v1/stock-operation/transfer/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 3,
    "quantity": 20,
    "from_location": 1,
    "to_location": 2,
    "comment": "Перемещение запаса бумаги в офис"
  }'
```

### Просмотр остатков

```bash
# Все остатки
curl -X GET http://localhost:8000/api/v1/stock/ \
  -H "Authorization: Bearer $TOKEN"

# Низкие остатки
curl -X GET http://localhost:8000/api/v1/stock/low_stock/ \
  -H "Authorization: Bearer $TOKEN"

# Остатки конкретного товара
curl -X GET "http://localhost:8000/api/v1/stock/?product=3" \
  -H "Authorization: Bearer $TOKEN"

# Остатки на конкретной локации
curl -X GET "http://localhost:8000/api/v1/stock/?location=1" \
  -H "Authorization: Bearer $TOKEN"
```

### История операций

```bash
# Все операции
curl -X GET http://localhost:8000/api/v1/stock-operation/ \
  -H "Authorization: Bearer $TOKEN"

# Операции по типу
curl -X GET "http://localhost:8000/api/v1/stock-operation/?operation_type=receipt" \
  -H "Authorization: Bearer $TOKEN"

# Операции с конкретным товаром
curl -X GET "http://localhost:8000/api/v1/stock-operation/?product=3" \
  -H "Authorization: Bearer $TOKEN"

# Операции за последний месяц (сортировка)
curl -X GET "http://localhost:8000/api/v1/stock-operation/?ordering=-timestamp" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Выдача и возврат

### Выдача техники сотруднику

```bash
# Выдать ноутбук
curl -X POST http://localhost:8000/api/v1/issues/create_issuance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 1,
    "recipient": "Иванов Иван Иванович",
    "issue_comment": "Выдан для работы в отделе продаж"
  }'

# Выдать монитор
curl -X POST http://localhost:8000/api/v1/issues/create_issuance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 3,
    "recipient": "Петров Петр Петрович",
    "issue_comment": "Дополнительный монитор для работы с графикой"
  }'
```

### Возврат техники

```bash
# Вернуть ноутбук
curl -X POST http://localhost:8000/api/v1/issues/1/return_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "return_comment": "Возврат в связи с окончанием проекта"
  }'

# Вернуть с проблемой
curl -X POST http://localhost:8000/api/v1/issues/2/return_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "return_comment": "Возврат для ремонта, не включается"
  }'
```

### Просмотр выдач

```bash
# Все выдачи
curl -X GET http://localhost:8000/api/v1/issues/ \
  -H "Authorization: Bearer $TOKEN"

# Только активные выдачи
curl -X GET http://localhost:8000/api/v1/issues/active/ \
  -H "Authorization: Bearer $TOKEN"

# Поиск по получателю
curl -X GET "http://localhost:8000/api/v1/issues/?recipient=Иванов" \
  -H "Authorization: Bearer $TOKEN"

# Фильтр по конкретному активу
curl -X GET "http://localhost:8000/api/v1/issues/?inventory_item=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Списание

### Списание расходника

```bash
# Списать просроченную бумагу
curl -X POST http://localhost:8000/api/v1/writeoffs/create_consumable/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 3,
    "quantity": 5,
    "location": 1,
    "reason": "Повреждение водой, непригодна для использования"
  }'

# Списать использованные картриджи
curl -X POST http://localhost:8000/api/v1/writeoffs/create_consumable/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 5,
    "quantity": 3,
    "location": 2,
    "reason": "Использованные картриджи, утилизация"
  }'
```

### Списание техники

```bash
# Списать неисправный ноутбук
curl -X POST http://localhost:8000/api/v1/writeoffs/create_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 2,
    "location": 1,
    "reason": "Неисправна материнская плата, экономически нецелесообразно ремонтировать"
  }'

# Списать устаревшую технику
curl -X POST http://localhost:8000/api/v1/writeoffs/create_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 5,
    "location": 1,
    "reason": "Моральное устаревание, замена на новую модель"
  }'
```

### Просмотр списаний

```bash
# Все списания
curl -X GET http://localhost:8000/api/v1/writeoffs/ \
  -H "Authorization: Bearer $TOKEN"

# Списания расходников
curl -X GET "http://localhost:8000/api/v1/writeoffs/?product__isnull=false" \
  -H "Authorization: Bearer $TOKEN"

# Списания техники
curl -X GET "http://localhost:8000/api/v1/writeoffs/?inventory_item__isnull=false" \
  -H "Authorization: Bearer $TOKEN"

# Списания за конкретную дату
curl -X GET "http://localhost:8000/api/v1/writeoffs/?date=2024-01-15" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Комплексные сценарии

### Сценарий 1: Прием новой партии техники

```bash
# 1. Создать товар (если еще не существует)
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Клавиатура Logitech K120",
    "sku": "KEYBOARD-LOGITECH-K120",
    "category": 1,
    "is_consumable": false,
    "description": "Проводная клавиатура для офисной работы"
  }'

# 2. Создать активы для 10 клавиатур
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/assets/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"product\": 6,
      \"serial_number\": \"LOGI-K120-$i\",
      \"inventory_number\": \"INV-2024-$(printf '%03d' $((100+$i)))\",
      \"current_location\": 1
    }"
done
```

### Сценарий 2: Оснащение нового сотрудника

```bash
# 1. Найти доступный ноутбук
curl -X GET "http://localhost:8000/api/v1/assets/available/?product=1" \
  -H "Authorization: Bearer $TOKEN"

# 2. Выдать ноутбук
curl -X POST http://localhost:8000/api/v1/issues/create_issuance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 1,
    "recipient": "Сидоров Сидор Сидорович",
    "issue_comment": "Выдан новому сотруднику IT отдела"
  }'

# 3. Найти доступную клавиатуру
curl -X GET "http://localhost:8000/api/v1/assets/available/?product=6" \
  -H "Authorization: Bearer $TOKEN"

# 4. Выдать клавиатуру
curl -X POST http://localhost:8000/api/v1/issues/create_issuance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 101,
    "recipient": "Сидоров Сидор Сидорович",
    "issue_comment": "Выдана вместе с ноутбуком"
  }'

# 5. Выдать расходники
curl -X POST http://localhost:8000/api/v1/stock-operation/expense/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 4,
    "quantity": 5,
    "from_location": 1,
    "comment": "Выдано новому сотруднику Сидорову С.С."
  }'
```

### Сценарий 3: Увольнение сотрудника

```bash
# 1. Найти все активные выдачи сотрудника
curl -X GET "http://localhost:8000/api/v1/issues/active/?recipient=Иванов" \
  -H "Authorization: Bearer $TOKEN"

# 2. Вернуть ноутбук
curl -X POST http://localhost:8000/api/v1/issues/1/return_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "return_comment": "Возвращено в связи с увольнением сотрудника"
  }'

# 3. Вернуть клавиатуру
curl -X POST http://localhost:8000/api/v1/issues/3/return_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "return_comment": "Возвращено в связи с увольнением сотрудника"
  }'
```

### Сценарий 4: Ежемесячная инвентаризация

```bash
# 1. Получить все остатки на складе
curl -X GET http://localhost:8000/api/v1/stock/ \
  -H "Authorization: Bearer $TOKEN" \
  > stock_report.json

# 2. Проверить низкие остатки
curl -X GET http://localhost:8000/api/v1/stock/low_stock/ \
  -H "Authorization: Bearer $TOKEN" \
  > low_stock_report.json

# 3. Получить список всей техники
curl -X GET http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer $TOKEN" \
  > assets_report.json

# 4. Получить активные выдачи
curl -X GET http://localhost:8000/api/v1/issues/active/ \
  -H "Authorization: Bearer $TOKEN" \
  > active_issues_report.json

# 5. Получить списания за месяц
curl -X GET "http://localhost:8000/api/v1/writeoffs/?date__gte=2024-01-01&date__lte=2024-01-31" \
  -H "Authorization: Bearer $TOKEN" \
  > writeoffs_report.json
```

### Сценарий 5: Замена неисправной техники

```bash
# 1. Сотрудник возвращает неисправный ноутбук
curl -X POST http://localhost:8000/api/v1/issues/1/return_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "return_comment": "Не включается, требует ремонта"
  }'

# 2. Отправить ноутбук на обслуживание
curl -X POST http://localhost:8000/api/v1/assets/1/mark_maintenance/ \
  -H "Authorization: Bearer $TOKEN"

# 3. Найти другой доступный ноутбук
curl -X GET "http://localhost:8000/api/v1/assets/available/?product=1" \
  -H "Authorization: Bearer $TOKEN"

# 4. Выдать замену
curl -X POST http://localhost:8000/api/v1/issues/create_issuance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 2,
    "recipient": "Иванов Иван Иванович",
    "issue_comment": "Замена неисправного ноутбука INV-2024-001"
  }'

# 5. Если ремонт невозможен - списать
curl -X POST http://localhost:8000/api/v1/writeoffs/create_asset/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_item": 1,
    "location": 1,
    "reason": "Неисправна материнская плата, ремонт нецелесообразен"
  }'
```

### Сценарий 6: Пополнение расходников по низким остаткам

```bash
# 1. Получить список товаров с низкими остатками
RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/stock/low_stock/ \
  -H "Authorization: Bearer $TOKEN")

echo $RESPONSE | jq '.results[] | {product: .product.name, quantity: .quantity, min_stock: .product.min_stock}'

# 2. Закупить товары
# Бумага А4 (текущий остаток: 8, минимум: 10, закупаем: 50)
curl -X POST http://localhost:8000/api/v1/stock-operation/receipt/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 3,
    "quantity": 50,
    "to_location": 1,
    "comment": "Пополнение по результатам проверки остатков"
  }'

# Ручки (текущий остаток: 45, минимум: 50, закупаем: 100)
curl -X POST http://localhost:8000/api/v1/stock-operation/receipt/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 4,
    "quantity": 100,
    "to_location": 1,
    "comment": "Пополнение по результатам проверки остатков"
  }'
```

---

## Python примеры (с использованием requests)

### Установка библиотеки

```bash
pip install requests
```

### Базовый класс для работы с API

```python
import requests
from typing import Dict, Optional

class OfficeAssetsAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.authenticate(username, password)

    def authenticate(self, username: str, password: str):
        """Получить JWT токен"""
        url = f"{self.base_url}/api/token/"
        response = requests.post(url, json={
            "username": username,
            "password": password
        })
        response.raise_for_status()
        data = response.json()
        self.token = data['access']

    def _headers(self) -> Dict[str, str]:
        """Заголовки с авторизацией"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str, params: Optional[Dict] = None):
        """GET запрос"""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict):
        """POST запрос"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self._headers(), json=data)
        response.raise_for_status()
        return response.json()

# Использование
api = OfficeAssetsAPI(
    base_url="http://localhost:8000",
    username="admin",
    password="password"
)

# Получить все товары
products = api.get("/api/v1/products/")
print(products)

# Создать категорию
category = api.post("/api/v1/categories/", {
    "name": "Мебель",
    "is_active": True
})
print(category)
```

### Пример: Автоматизация поступления товаров

```python
import csv
from officeassets_api import OfficeAssetsAPI

api = OfficeAssetsAPI(
    base_url="http://localhost:8000",
    username="admin",
    password="password"
)

# Читаем CSV с данными о поступлении
with open('receipt.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Создаем операцию прихода
        result = api.post("/api/v1/stock-operation/receipt/", {
            "product": int(row['product_id']),
            "quantity": float(row['quantity']),
            "to_location": int(row['location_id']),
            "comment": row['comment']
        })
        print(f"Создана операция прихода: {result['id']}")
```

---

## JavaScript примеры (Fetch API)

```javascript
class OfficeAssetsAPI {
    constructor(baseUrl, username, password) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = null;
        this.authenticate(username, password);
    }

    async authenticate(username, password) {
        const response = await fetch(`${this.baseUrl}/api/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        this.token = data.access;
    }

    async get(endpoint, params = {}) {
        const url = new URL(`${this.baseUrl}${endpoint}`);
        Object.keys(params).forEach(key =>
            url.searchParams.append(key, params[key])
        );

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        return await response.json();
    }

    async post(endpoint, data) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    }
}

// Использование
const api = new OfficeAssetsAPI(
    'http://localhost:8000',
    'admin',
    'password'
);

// Получить низкие остатки
api.get('/api/v1/stock/low_stock/')
    .then(data => console.log(data));

// Создать выдачу
api.post('/api/v1/issues/create_issuance/', {
    inventory_item: 1,
    recipient: 'Иванов И.И.',
    issue_comment: 'Тестовая выдача'
}).then(data => console.log(data));
```

---

Эти примеры покрывают основные сценарии использования API OfficeAssets. Для получения полной информации обратитесь к [Swagger документации](http://localhost:8000/api/v1/docs/).
