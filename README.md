# 📱 SMS Анализатор - Сервис автоматического перенаправления SMS

**SMS Анализатор** — это профессиональный веб-сервис для автоматического получения, анализа и перенаправления SMS сообщений в Telegram каналы/группы. Система поддерживает интеграцию с популярными SMS провайдерами и предоставляет удобный веб-интерфейс для управления правилами переадресации.

## 🚀 Основные возможности

### 📡 Поддержка SMS провайдеров
- **Novofon** - интеграция через webhook API
- **Telfin** - поддержка API ключей
- **Mango** - поддержка API ключей

### 🤖 Telegram бот
- Автоматическая регистрация пользователей через номер телефона
- Добавление Telegram каналов/групп для получения уведомлений
- Генерация безопасных паролей для новых пользователей

### ⚙️ Система правил
- Настройка правил перенаправления по отправителю SMS
- Поддержка маски "Любой отправитель"
- Привязка номеров к конкретным Telegram каналам
- Фильтрация сообщений по содержимому

### 🌐 Веб-интерфейс
- Современный адаптивный интерфейс
- Управление API ключами провайдеров
- Настройка правил переадресации
- Просмотр статистики и логов

### 🔐 Безопасность
- JWT авторизация для API
- Уникальные webhook токены для каждого пользователя
- Защищенные эндпоинты
- Валидация входящих данных

## 🛠 Технологический стек

### Backend
- **Django 5.1.3** - веб-фреймворк
- **Django REST Framework** - API
- **MySQL** - база данных
- **python-telegram-bot** - Telegram бот

### Frontend
- **Bootstrap 5** - UI фреймворк
- **JavaScript/jQuery** - интерактивность
- **HTML5/CSS3** - верстка

### Дополнительные библиотеки
- **drf-yasg** - автогенерация документации API
- **python-dotenv** - управление переменными окружения
- **httpx** - HTTP клиент
- **loguru** - логирование

## 📦 Установка и запуск

### Требования к системе
- Python 3.8+
- MySQL 8.0+
- Git

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-repo/sms-analizator-service.git
cd sms-analizator-service
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```bash
# База данных
DB_NAME=sms_analyzer
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Telegram Bot
TOKEN_BOT=your_telegram_bot_token

# Django
SECRET_KEY=your_secret_key
DEBUG=True
```

### 5. Настройка базы данных
```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

### 6. Запуск сервера
```bash
# Веб-сервер
python manage.py runserver

# Telegram бот (в отдельном терминале)
python manage.py run_bot
```

## 📖 Использование

### Регистрация через Telegram бота

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Нажмите кнопку "Отправить номер телефона"
4. Получите логин и пароль для веб-интерфейса

### Настройка SMS провайдеров

#### Novofon
1. Войдите в личный кабинет Novofon
2. Настройте webhook URL: `https://your-domain.com/webhook/{ваш_токен}/`
3. В веб-интерфейсе добавьте номер телефона в разделе "Сервисы"

#### Telfin/Mango
1. Получите API ключ от провайдера
2. В веб-интерфейсе добавьте ключ в разделе "Сервисы"
3. Настройте webhook в личном кабинете провайдера

### Создание правил переадресации

1. Перейдите в раздел "Правила"
2. Выберите номер телефона (источник)
3. Укажите отправителя или выберите "Любой отправитель"
4. Выберите Telegram канал для уведомлений
5. Сохраните правило

### Добавление Telegram каналов

1. Добавьте бота в ваш канал/группу как администратора
2. Отправьте команду `/start` в канале
3. Канал автоматически добавится в ваш аккаунт

## 🔧 API Documentation

### Аутентификация
```bash
POST /auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

### Регистрация
```bash
POST /auth/registration/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

### Webhook для SMS
```bash
POST /webhook/{token}/
Content-Type: application/json

{
    "result": {
        "caller_did": "+71234567890",
        "caller_id": "SENDER",
        "text": "SMS text content"
    }
}
```

### Автоматическая документация API
Доступна по адресу: `http://localhost:8000/swagger/`

## 🏗 Архитектура системы

### Структура проекта
```
sms-analizator-service/
├── sms_analizator_service/     # Основные настройки Django
├── users_app/                  # Приложение пользователей
│   ├── api/                   # API эндпоинты
│   ├── management/commands/   # Django команды
│   ├── models.py             # Модели данных
│   ├── views.py              # Веб-представления
│   └── telegram_bot.py       # Telegram бот
├── utils/                     # Утилиты
├── templates/                 # HTML шаблоны и статика
└── requirements.txt          # Зависимости
```

### Модели данных

- **User** - пользователи системы (расширенная модель Django)
- **Key** - API ключи SMS провайдеров
- **NumbersService** - номера телефонов пользователей
- **TelegramChats** - Telegram каналы/группы
- **Rules** - правила переадресации SMS

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
python manage.py test

# Конкретное приложение
python manage.py test users_app

# С покрытием кода
coverage run --source='.' manage.py test
coverage report
```

### Ключевые тест-кейсы
- Регистрация и аутентификация пользователей
- Создание и применение правил переадресации
- Обработка webhook запросов от SMS провайдеров
- Отправка уведомлений в Telegram
- Валидация API ключей

## 📊 Мониторинг и логирование

### Логирование
Система использует `loguru` для структурированного логирования:
- Уровни: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Ротация логов по размеру и времени
- Отдельные файлы для разных компонентов

### Метрики
- Количество обработанных SMS
- Статистика по провайдерам
- Активность пользователей
- Производительность API

## 🚀 Развертывание в продакшене

### Docker (рекомендуется)
```dockerfile
# Dockerfile включен в проект
docker build -t sms-analyzer .
docker run -p 8000:8000 sms-analyzer
```

### Systemd сервисы
```bash
# Веб-сервер
sudo systemctl enable sms-analyzer-web
sudo systemctl start sms-analyzer-web

# Telegram бот
sudo systemctl enable sms-analyzer-bot
sudo systemctl start sms-analyzer-bot
```

### Nginx конфигурация
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/static/files/;
    }
}
```

## 🛡 Безопасность

### Рекомендации по безопасности
1. Используйте HTTPS в продакшене
2. Регулярно обновляйте зависимости
3. Настройте файрвол для ограничения доступа
4. Используйте сильные пароли для базы данных
5. Настройте резервное копирование

### Переменные окружения продакшена
```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

## 📈 Масштабирование

### Горизонтальное масштабирование
- Использование Redis для кеширования
- Настройка Load Balancer
- Разделение базы данных (master-slave)
- Использование Celery для фоновых задач

### Потенциальные узкие места
- Обработка большого количества webhook запросов
- Отправка уведомлений в Telegram (rate limits)
- Размер базы данных при большом объеме SMS

## 🤝 Вклад в разработку

### Порядок внесения изменений
1. Fork репозитория
2. Создайте feature ветку
3. Внесите изменения с тестами
4. Убедитесь в прохождении всех тестов
5. Создайте Pull Request

### Стандарты кода
- Следование PEP 8
- Покрытие кода тестами >80%
- Документирование новых функций
- Использование типизации (typing)

## 📞 Поддержка

### Контакты
- Email: support@your-domain.com
- Telegram: @your_support_bot
- GitHub Issues: [Создать задачу](https://github.com/your-repo/issues)

### FAQ
- **Q: Как добавить нового SMS провайдера?**
  A: Создайте новый тип в `KEY_TYPES` и реализуйте соответствующий API клиент

- **Q: Можно ли ограничить количество правил?**
  A: Да, добавьте валидацию в модель `Rules`

- **Q: Как настроить уведомления по email?**
  A: Настройте SMTP в `settings.py` и добавьте соответствующие обработчики

## 📜 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 🗓 Changelog

### v1.0.0 (2024-01-01)
- Первый релиз
- Поддержка Novofon, Telfin, Mango
- Telegram бот
- Веб-интерфейс
- API документация

---

Создано с ❤️ для автоматизации SMS уведомлений 