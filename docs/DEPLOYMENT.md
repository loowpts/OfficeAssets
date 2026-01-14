# Руководство по развертыванию OfficeAssets

## Содержание
- [Требования к системе](#требования-к-системе)
- [Локальная разработка](#локальная-разработка)
- [Production развертывание](#production-развертывание)
- [Docker развертывание](#docker-развертывание)
- [Настройка CI/CD](#настройка-cicd)
- [Мониторинг и логи](#мониторинг-и-логи)
- [Резервное копирование](#резервное-копирование)
- [Устранение неполадок](#устранение-неполадок)

---

## Требования к системе

### Минимальные требования (Development)

- **OS**: Linux / macOS / Windows
- **Python**: 3.11 или выше
- **RAM**: 2 GB
- **Disk**: 5 GB свободного места
- **Redis**: 6.0+
- **PostgreSQL**: 13+ (опционально для dev)

### Рекомендуемые требования (Production)

- **OS**: Ubuntu 20.04 LTS / 22.04 LTS
- **Python**: 3.11
- **RAM**: 4 GB минимум, 8 GB рекомендуется
- **CPU**: 2 ядра минимум, 4 ядра рекомендуется
- **Disk**: 50 GB (с учетом логов и резервных копий)
- **Redis**: 6.0+
- **PostgreSQL**: 14+
- **Nginx**: 1.18+

---

## Локальная разработка

### Шаг 1: Установка зависимостей

#### Ubuntu/Debian
```bash
# Обновить пакеты
sudo apt update && sudo apt upgrade -y

# Установить Python и зависимости
sudo apt install python3.11 python3.11-venv python3-pip -y

# Установить Redis
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Установить PostgreSQL (опционально)
sudo apt install postgresql postgresql-contrib -y
```

#### macOS
```bash
# Установить Homebrew (если еще не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установить Python
brew install python@3.11

# Установить Redis
brew install redis
brew services start redis

# Установить PostgreSQL (опционально)
brew install postgresql@14
brew services start postgresql@14
```

### Шаг 2: Клонирование и настройка проекта

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/OfficeAssets.git
cd OfficeAssets

# Создать виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Создать .env файл
cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
REDIS_URL=redis://127.0.0.1:6379/1
STATIC_ROOT=staticfiles
MEDIA_ROOT=media
EOF
```

### Шаг 3: Настройка базы данных

#### SQLite (для быстрого старта)
```bash
# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Загрузить тестовые данные (опционально)
# python manage.py loaddata fixtures/initial_data.json
```

#### PostgreSQL (рекомендуется)
```bash
# Создать базу данных и пользователя
sudo -u postgres psql << EOF
CREATE DATABASE officeassets;
CREATE USER officeassetsuser WITH PASSWORD 'your_secure_password';
ALTER ROLE officeassetsuser SET client_encoding TO 'utf8';
ALTER ROLE officeassetsuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE officeassetsuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE officeassets TO officeassetsuser;
\q
EOF

# Обновить .env
echo "DATABASE_URL=postgresql://officeassetsuser:your_secure_password@localhost:5432/officeassets" >> .env

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser
```

### Шаг 4: Запуск сервера разработки

```bash
# Терминал 1: Django сервер
python manage.py runserver

# Терминал 2: Celery worker
celery -A settings worker -l info

# Терминал 3: Celery beat
celery -A settings beat -l info
```

Приложение доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

API документация: [http://127.0.0.1:8000/api/v1/docs/](http://127.0.0.1:8000/api/v1/docs/)

---

## Production развертывание

### Архитектура production

```
                       Internet
                          │
                          ▼
                   ┌──────────────┐
                   │   Nginx      │ :80, :443 (SSL)
                   │  (Reverse    │
                   │   Proxy)     │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Gunicorn    │ :8000
                   │  (WSGI)      │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   Django     │
                   │  Application │
                   └──┬────────┬──┘
                      │        │
         ┌────────────┘        └─────────────┐
         ▼                                   ▼
  ┌──────────────┐                    ┌──────────────┐
  │ PostgreSQL   │                    │    Redis     │
  │   Database   │                    │    Cache     │
  └──────────────┘                    └──────┬───────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │    Celery    │
                                      │ Worker+Beat  │
                                      └──────────────┘
```

### Шаг 1: Подготовка сервера (Ubuntu 22.04)

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить необходимые пакеты
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    nginx supervisor git

# Создать пользователя для приложения
sudo useradd -m -s /bin/bash officeassets
sudo usermod -aG sudo officeassets

# Переключиться на пользователя
sudo su - officeassets
```

### Шаг 2: Развертывание приложения

```bash
# Клонировать репозиторий
cd /home/officeassets
git clone https://github.com/yourusername/OfficeAssets.git app
cd app

# Создать виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Создать production .env
cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://officeassetsuser:secure_password@localhost:5432/officeassets
REDIS_URL=redis://127.0.0.1:6379/1
STATIC_ROOT=/home/officeassets/app/staticfiles
MEDIA_ROOT=/home/officeassets/app/media
EOF
```

### Шаг 3: Настройка PostgreSQL

```bash
# Создать базу данных (от root)
exit  # Выйти из пользователя officeassets
sudo -u postgres psql << EOF
CREATE DATABASE officeassets;
CREATE USER officeassetsuser WITH PASSWORD 'secure_password_here';
ALTER ROLE officeassetsuser SET client_encoding TO 'utf8';
ALTER ROLE officeassetsuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE officeassetsuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE officeassets TO officeassetsuser;
\q
EOF

# Вернуться к пользователю
sudo su - officeassets
cd app
source venv/bin/activate

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Собрать статические файлы
python manage.py collectstatic --noinput

# Создать необходимые директории
mkdir -p logs media
```

### Шаг 4: Настройка Gunicorn

```bash
# Создать конфигурационный файл
cat > gunicorn_config.py << EOF
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Логирование
accesslog = "/home/officeassets/app/logs/gunicorn_access.log"
errorlog = "/home/officeassets/app/logs/gunicorn_error.log"
loglevel = "info"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
EOF

# Тестовый запуск
gunicorn settings.wsgi:application -c gunicorn_config.py
# Ctrl+C для остановки
```

### Шаг 5: Настройка Supervisor

```bash
# Выйти из пользователя officeassets
exit

# Создать конфигурацию для Django (Gunicorn)
sudo tee /etc/supervisor/conf.d/officeassets.conf > /dev/null << EOF
[program:officeassets]
command=/home/officeassets/app/venv/bin/gunicorn settings.wsgi:application -c /home/officeassets/app/gunicorn_config.py
directory=/home/officeassets/app
user=officeassets
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/officeassets/app/logs/supervisor_gunicorn.log
EOF

# Создать конфигурацию для Celery Worker
sudo tee /etc/supervisor/conf.d/officeassets-celery.conf > /dev/null << EOF
[program:officeassets-celery]
command=/home/officeassets/app/venv/bin/celery -A settings worker -l info
directory=/home/officeassets/app
user=officeassets
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/officeassets/app/logs/supervisor_celery.log
EOF

# Создать конфигурацию для Celery Beat
sudo tee /etc/supervisor/conf.d/officeassets-celerybeat.conf > /dev/null << EOF
[program:officeassets-celerybeat]
command=/home/officeassets/app/venv/bin/celery -A settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/home/officeassets/app
user=officeassets
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/officeassets/app/logs/supervisor_celerybeat.log
EOF

# Обновить и запустить supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

### Шаг 6: Настройка Nginx

```bash
# Создать конфигурацию Nginx
sudo tee /etc/nginx/sites-available/officeassets > /dev/null << 'EOF'
upstream officeassets_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /home/officeassets/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/officeassets/app/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://officeassets_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
EOF

# Создать символическую ссылку
sudo ln -s /etc/nginx/sites-available/officeassets /etc/nginx/sites-enabled/

# Удалить дефолтную конфигурацию
sudo rm /etc/nginx/sites-enabled/default

# Проверить конфигурацию
sudo nginx -t

# Перезапустить Nginx
sudo systemctl restart nginx
```

### Шаг 7: Настройка SSL (Let's Encrypt)

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить SSL сертификат
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Проверить автообновление
sudo systemctl status certbot.timer

# Тест обновления
sudo certbot renew --dry-run
```

После установки SSL, Nginx конфигурация автоматически обновится для поддержки HTTPS.

### Шаг 8: Настройка Firewall

```bash
# Установить UFW
sudo apt install ufw -y

# Разрешить SSH
sudo ufw allow OpenSSH

# Разрешить HTTP и HTTPS
sudo ufw allow 'Nginx Full'

# Включить firewall
sudo ufw enable

# Проверить статус
sudo ufw status
```

---

## Docker развертывание

### Создание Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создать директорию приложения
WORKDIR /app

# Копировать зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копировать приложение
COPY . .

# Создать необходимые директории
RUN mkdir -p logs media staticfiles

# Собрать статические файлы
RUN python manage.py collectstatic --noinput

# Открыть порт
EXPOSE 8000

# Команда по умолчанию
CMD ["gunicorn", "settings.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Создание docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: officeassets
      POSTGRES_USER: officeassetsuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  web:
    build: .
    command: gunicorn settings.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - ./:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env.docker
    depends_on:
      - db
      - redis
    restart: always

  celery:
    build: .
    command: celery -A settings worker -l info
    volumes:
      - ./:/app
    env_file:
      - .env.docker
    depends_on:
      - db
      - redis
    restart: always

  celery-beat:
    build: .
    command: celery -A settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./:/app
    env_file:
      - .env.docker
    depends_on:
      - db
      - redis
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Создание .env.docker

```bash
cat > .env.docker << EOF
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://officeassetsuser:\${DB_PASSWORD}@db:5432/officeassets
REDIS_URL=redis://redis:6379/1
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media
EOF
```

### Запуск с Docker

```bash
# Создать .env файл с паролем БД
echo "DB_PASSWORD=your_secure_password" > .env

# Собрать и запустить
docker-compose up -d

# Применить миграции
docker-compose exec web python manage.py migrate

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser

# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down
```

---

## Настройка CI/CD

### GitHub Actions

Создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      run: |
        python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest

    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /home/officeassets/app
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          python manage.py migrate
          python manage.py collectstatic --noinput
          sudo supervisorctl restart officeassets officeassets-celery officeassets-celerybeat
```

---

## Мониторинг и логи

### Просмотр логов

```bash
# Django логи
tail -f /home/officeassets/app/logs/django.log

# Gunicorn логи
tail -f /home/officeassets/app/logs/gunicorn_error.log

# Nginx логи
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Supervisor логи
sudo tail -f /home/officeassets/app/logs/supervisor_*.log
```

### Мониторинг с Prometheus и Grafana (опционально)

```bash
# Установить prometheus_client
pip install django-prometheus

# Добавить в settings.py
INSTALLED_APPS += ['django_prometheus']

# Добавить middleware
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... другие middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

---

## Резервное копирование

### Автоматическое резервное копирование базы данных

```bash
# Создать скрипт backup.sh
cat > /home/officeassets/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/officeassets/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="officeassets"
DB_USER="officeassetsuser"

mkdir -p $BACKUP_DIR

# Backup базы данных
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Backup медиа файлов
tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz /home/officeassets/app/media

# Удалить старые бэкапы (старше 30 дней)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x /home/officeassets/backup.sh

# Добавить в crontab (ежедневно в 2:00)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/officeassets/backup.sh") | crontab -
```

### Восстановление из бэкапа

```bash
# Восстановить базу данных
gunzip -c /home/officeassets/backups/db_20240115_020000.sql.gz | psql -U officeassetsuser -d officeassets

# Восстановить медиа файлы
tar -xzf /home/officeassets/backups/media_20240115_020000.tar.gz -C /
```

---

## Устранение неполадок

### Приложение не запускается

```bash
# Проверить статус всех сервисов
sudo supervisorctl status

# Проверить логи
tail -f /home/officeassets/app/logs/gunicorn_error.log

# Перезапустить сервисы
sudo supervisorctl restart all
```

### Ошибки базы данных

```bash
# Проверить подключение к PostgreSQL
psql -U officeassetsuser -d officeassets -c "SELECT 1;"

# Проверить миграции
cd /home/officeassets/app
source venv/bin/activate
python manage.py showmigrations
```

### Celery не работает

```bash
# Проверить статус Redis
redis-cli ping

# Проверить Celery worker
sudo supervisorctl status officeassets-celery

# Проверить логи
tail -f /home/officeassets/app/logs/supervisor_celery.log
```

### Nginx ошибки

```bash
# Проверить конфигурацию
sudo nginx -t

# Проверить статус
sudo systemctl status nginx

# Перезапустить
sudo systemctl restart nginx
```

### Высокая нагрузка

```bash
# Проверить использование ресурсов
htop

# Проверить количество worker'ов Gunicorn
ps aux | grep gunicorn | wc -l

# Увеличить количество worker'ов
# Отредактировать gunicorn_config.py и перезапустить
```

---

## Обновление приложения

```bash
# Переключиться на пользователя
sudo su - officeassets
cd app

# Создать бэкап
/home/officeassets/backup.sh

# Обновить код
git pull origin main

# Активировать виртуальное окружение
source venv/bin/activate

# Обновить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Собрать статические файлы
python manage.py collectstatic --noinput

# Перезапустить сервисы
exit
sudo supervisorctl restart all
```

---

## Чеклист после развертывания

- [ ] Приложение доступно по HTTPS
- [ ] SSL сертификат настроен и действителен
- [ ] Все сервисы запущены (Gunicorn, Celery, Nginx)
- [ ] Миграции применены
- [ ] Статические файлы собраны
- [ ] Суперпользователь создан
- [ ] Firewall настроен
- [ ] Резервное копирование настроено
- [ ] Логи пишутся корректно
- [ ] API документация доступна
- [ ] Celery задачи выполняются

---

## Полезные команды

```bash
# Перезапустить все сервисы
sudo supervisorctl restart all

# Проверить статус всех сервисов
sudo supervisorctl status

# Просмотр логов в реальном времени
sudo supervisorctl tail -f officeassets stderr

# Очистка старых логов
find /home/officeassets/app/logs -type f -mtime +30 -delete

# Проверка использования диска
df -h

# Проверка свободной памяти
free -h
```

---

Следуя этому руководству, вы успешно развернете OfficeAssets в production окружении с высокой степенью надежности и безопасности.
