# 🛍 Telegram Catalog Bot

Telegram-бот с каталогом товаров через Mini App. Пользователи регистрируются, просматривают каталог и оставляют заявки. Заявки уходят в группу администраторов.

---

## 📁 Структура проекта

```
tg_catalog_bot/
├── bot/
│   ├── main.py              # Точка входа бота
│   ├── config.py            # Конфигурация
│   ├── handlers.py          # Регистрация и главное меню
│   └── handlers_orders.py   # Обработка заявок из Mini App
├── database/
│   └── db.py                # SQLite: инициализация и запросы
├── admin/
│   ├── admin_app.py         # FastAPI админ-панель + API для Mini App
│   └── templates/           # HTML-шаблоны админки
│       ├── base.html
│       ├── index.html
│       ├── products.html
│       ├── edit_product.html
│       ├── users.html
│       └── orders.html
├── miniapp/
│   └── index.html           # Telegram Mini App (каталог)
├── .env.example             # Шаблон переменных окружения
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

---

## ⚙️ Установка и запуск

### 1. Клонируйте и настройте окружение

```bash
cd tg_catalog_bot
cp .env.example .env
# Откройте .env и заполните все значения
```

### 2. Заполните .env

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `ADMIN_GROUP_ID` | ID группы для уведомлений (со знаком `-`) |
| `ADMIN_IDS` | Telegram ID администраторов через запятую |
| `MINI_APP_URL` | HTTPS-URL вашего Mini App |

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Разместите Mini App

Файл `miniapp/index.html` необходимо разместить на HTTPS-хостинге.  
Варианты: GitHub Pages, Vercel, Nginx на вашем сервере.

```
https://yourdomain.com/miniapp/index.html
```

Этот URL прописывается в `MINI_APP_URL` в `.env`.

### 5. Запустите бота

```bash
python bot/main.py
```

### 6. Запустите админ-панель

```bash
uvicorn admin.admin_app:app --host 0.0.0.0 --port 8000
```

Админка доступна по адресу: `http://localhost:8000/admin`

---

## 🐳 Docker (рекомендуется для продакшена)

```bash
cp .env.example .env
# заполните .env
docker-compose up -d
```

---

## 🔧 Настройка BotFather

1. Создайте бота: `/newbot`
2. Включите Menu Button с Mini App:
   ```
   /setmenubutton → выберите бота → Web App URL → вставьте MINI_APP_URL
   ```
   Или оставьте как есть — кнопка появляется автоматически после регистрации.

---

## 📊 Функционал

### Бот (пользователь)
- `/start` — регистрация (имя + телефон)
- Кнопка **"Открыть каталог"** → Mini App
- После выбора товаров → заявка → уведомление в группу администраторов

### Mini App (каталог)
- Сетка товаров с фото, ценой, артикулом
- Мультивыбор с визуальным выделением
- Кнопка "Отправить заявку" с количеством выбранных

### Админ-панель (`/admin`)
- Дашборд со статистикой
- Управление товарами: добавить / редактировать / удалить
- Загрузка фото для товаров
- Импорт товаров из Excel (.xlsx)
- Скачать шаблон Excel для импорта
- Список клиентов
- Список заявок с поиском

---

## 📋 Импорт товаров из Excel

Скачайте шаблон: `http://localhost:8000/admin/excel-template`

Формат файла:

| Название | Описание | Цена | Артикул |
|---|---|---|---|
| Товар 1 | Описание | 1500 | ART-001 |

Фото загружаются вручную через карточку товара в админке.

---

## 🔗 API эндпоинты

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/products` | Список товаров (для Mini App) |
| GET | `/admin` | Дашборд |
| GET | `/admin/products` | Управление товарами |
| POST | `/admin/products/add` | Добавить товар |
| POST | `/admin/products/{id}/edit` | Редактировать товар |
| POST | `/admin/products/{id}/delete` | Удалить товар |
| POST | `/admin/products/import` | Импорт из Excel |
| GET | `/admin/excel-template` | Скачать шаблон Excel |
| GET | `/admin/users` | Список клиентов |
| GET | `/admin/orders` | Список заявок |
