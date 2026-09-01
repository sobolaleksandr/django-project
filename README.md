# Task Manager API

Система управления задачами на Django + Django REST Framework: задачи, назначение исполнителей, отметка о выполнении и комментарии. Авторизация — JWT, документация — Swagger UI и Redoc.

## Возможности

- Регистрация пользователей и JWT-авторизация (access/refresh).
- Создание, просмотр, редактирование и удаление задач.
- Назначение задачи другому пользователю и снятие исполнителя.
- Отметка задачи выполненной и возврат её в работу.
- Комментирование задач с правами на редактирование только своих комментариев.
- Фильтрация, полнотекстовый поиск и сортировка списка задач, пагинация.
- Админка Django для всех сущностей.

## Стек

| Компонент | Версия |
|---|---|
| Python | 3.10+ |
| Django | 5.2 |
| Django REST Framework | 3.18 |
| djangorestframework-simplejwt | 5.5 |
| drf-spectacular (OpenAPI 3) | 0.30 |
| django-filter | 26.1 |
| БД | SQLite (по умолчанию) / PostgreSQL 16 |
| Тесты | pytest, pytest-django, factory-boy |
| Линтер и форматтер | ruff |

## Быстрый старт (SQLite, без Docker)

```bash
git clone https://github.com/sobolaleksandr/django-project.git
cd django-project

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env
python manage.py migrate
python manage.py seed_demo         # демо-данные, опционально
python manage.py createsuperuser   # доступ в админку, опционально
python manage.py runserver
```

Приложение поднимется на http://127.0.0.1:8000/.

Демо-пользователи после `seed_demo`: `alice`, `bob`, `carol` с паролем `DemoPassw0rd!`.

Те же шаги через Makefile: `make install && make migrate && make seed && make run`.

## Запуск в Docker (PostgreSQL)

```bash
docker compose up --build
```

Поднимаются два сервиса: `db` (PostgreSQL 16) и `web` (Django под gunicorn, миграции применяются автоматически). API доступно на http://localhost:8000/.

Остановить и удалить данные: `docker compose down -v`.

## Переменные окружения

Задаются в `.env` (см. `.env.example`):

| Переменная | Назначение | Значение по умолчанию |
|---|---|---|
| `SECRET_KEY` | секретный ключ Django | ключ для разработки |
| `DEBUG` | режим отладки | `False` |
| `ALLOWED_HOSTS` | список хостов через запятую | `localhost,127.0.0.1,0.0.0.0` |
| `DATABASE_URL` | строка подключения к БД | `sqlite:///db.sqlite3` |

Для PostgreSQL: `DATABASE_URL=postgres://taskuser:taskpass@localhost:5432/taskdb`.

## Документация API

| Ресурс | Адрес |
|---|---|
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| Redoc | http://127.0.0.1:8000/api/redoc/ |
| Схема OpenAPI 3 | http://127.0.0.1:8000/api/schema/ |
| Админка | http://127.0.0.1:8000/admin/ |

В Swagger UI нажмите **Authorize** и вставьте `Bearer <access-токен>`.

## Эндпоинты

Базовый префикс — `/api/v1/`. Все эндпоинты, кроме регистрации и получения токена, требуют заголовок `Authorization: Bearer <access>`.

### Авторизация

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/auth/register/` | регистрация пользователя |
| `POST` | `/auth/token/` | получение пары access/refresh |
| `POST` | `/auth/token/refresh/` | обновление access-токена |
| `POST` | `/auth/token/verify/` | проверка токена |

### Пользователи

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/users/` | список пользователей (для выбора исполнителя), поиск `?search=` |
| `GET` | `/users/{id}/` | карточка пользователя |
| `GET` | `/users/me/` | текущий пользователь |

### Задачи

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/tasks/` | список задач |
| `POST` | `/tasks/` | создать задачу |
| `GET` | `/tasks/{id}/` | задача вместе с комментариями |
| `PUT` / `PATCH` | `/tasks/{id}/` | изменить задачу (только автор) |
| `DELETE` | `/tasks/{id}/` | удалить задачу (только автор) |
| `POST` | `/tasks/{id}/assign/` | назначить исполнителя (автор или исполнитель) |
| `POST` | `/tasks/{id}/complete/` | отметить выполненной (автор или исполнитель) |
| `POST` | `/tasks/{id}/reopen/` | вернуть в работу (автор или исполнитель) |

Параметры списка задач:

- фильтры: `status` (`todo`, `in_progress`, `done`), `priority` (`low`, `medium`, `high`), `author`, `assignee`, `is_assigned`, `due_before`, `due_after`;
- поиск: `search` по названию и описанию;
- сортировка: `ordering` по `created_at`, `updated_at`, `due_date`, `priority`, `status` (с минусом — по убыванию);
- пагинация: `page`, по 20 записей на страницу.

### Комментарии

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/tasks/{task_id}/comments/` | комментарии задачи |
| `POST` | `/tasks/{task_id}/comments/` | добавить комментарий |
| `GET` | `/comments/{id}/` | комментарий |
| `PUT` / `PATCH` | `/comments/{id}/` | изменить свой комментарий |
| `DELETE` | `/comments/{id}/` | удалить свой комментарий |

## Права доступа

| Действие | Кто может |
|---|---|
| Просмотр задач и комментариев | любой авторизованный пользователь |
| Создание задачи | любой авторизованный пользователь |
| Редактирование и удаление задачи | только автор задачи |
| Назначение исполнителя, `complete`, `reopen` | автор задачи или её текущий исполнитель |
| Создание комментария | любой авторизованный пользователь |
| Редактирование и удаление комментария | только автор комментария |

Принятые допущения: в ТЗ нет команд и проектов, поэтому задачи видны всем авторизованным пользователям — иначе назначить задачу коллеге было бы невозможно. Автор задачи фиксируется по токену и не может быть переопределён через тело запроса.

## Пример сценария (curl)

```bash
BASE=http://127.0.0.1:8000/api/v1

# 1. Регистрация
curl -X POST $BASE/auth/register/ -H 'Content-Type: application/json' -d '{
  "username": "demo",
  "email": "demo@example.com",
  "password": "StrongPassw0rd!",
  "password_confirm": "StrongPassw0rd!"
}'

# 2. Получение токена
TOKEN=$(curl -s -X POST $BASE/auth/token/ -H 'Content-Type: application/json' \
  -d '{"username": "demo", "password": "StrongPassw0rd!"}' | python -c "import sys,json;print(json.load(sys.stdin)['access'])")

# 3. Создание задачи
curl -X POST $BASE/tasks/ -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{
  "title": "Проверить API",
  "description": "Сквозной сценарий",
  "priority": "high"
}'

# 4. Назначение исполнителя (id берётся из GET /users/)
curl -X POST $BASE/tasks/1/assign/ -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"assignee_id": 2}'

# 5. Комментарий
curl -X POST $BASE/tasks/1/comments/ -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"text": "Начинаю проверку"}'

# 6. Отметка о выполнении
curl -X POST $BASE/tasks/1/complete/ -H "Authorization: Bearer $TOKEN"

# 7. Фильтрация выполненных задач
curl "$BASE/tasks/?status=done&ordering=-updated_at" -H "Authorization: Bearer $TOKEN"
```

## Тестирование

```bash
pytest                                  # весь набор тестов
pytest --cov --cov-report=term-missing  # с отчётом о покрытии
pytest apps/tasks -k complete           # выборочный запуск
```

58 тестов, покрытие кода приложений — 100%. Тесты выполняются на отдельной тестовой БД и охватывают:

- регистрацию, выдачу и обновление токенов, отказ анонимному пользователю;
- CRUD задач, фильтры, поиск, сортировку, пагинацию;
- назначение исполнителя, `complete` и `reopen`, включая проверку прав;
- CRUD комментариев и права на чужие комментарии;
- бизнес-логику моделей (идемпотентность `mark_completed`, просроченность, каскадные удаления).

## Качество кода

```bash
ruff check .           # линтер (PEP 8, isort, bugbear и др.)
ruff format --check .  # проверка форматирования
ruff format .          # автоформатирование
```

Или через Makefile: `make lint`, `make format`.

GitHub Actions (`.github/workflows/ci.yml`) прогоняет линтер, системные проверки Django и тесты на каждый push и pull request.

## Структура проекта

```
config/                     настройки Django, корневые URL, WSGI/ASGI
apps/
  users/                    кастомная модель User, регистрация, JWT-роуты, профиль
    tests/                  тесты авторизации и пользователей
  tasks/
    models.py               Task и Comment с бизнес-логикой статусов
    serializers.py          сериализаторы задач и комментариев
    permissions.py          IsAuthorOrReadOnly, IsAuthorOrAssignee
    filters.py              FilterSet для списка задач
    views.py                TaskViewSet и вьюхи комментариев
    management/commands/    seed_demo — демо-данные
    tests/                  тесты моделей, задач, действий и комментариев
conftest.py                 общие фикстуры pytest
requirements.txt            зависимости приложения
requirements-dev.txt        зависимости для тестов и линтера
pyproject.toml              конфигурация ruff, pytest и coverage
Dockerfile, docker-compose.yml
Makefile
```

## Модель данных

**Task** — `title`, `description`, `status` (`todo` / `in_progress` / `done`), `priority` (`low` / `medium` / `high`), `author`, `assignee`, `due_date`, `completed_at`, `created_at`, `updated_at`. Удаление автора удаляет его задачи, удаление исполнителя лишь снимает назначение.

**Comment** — `task`, `author`, `text`, `created_at`, `updated_at`. Удаляется вместе с задачей.

**User** — расширяет `AbstractUser`, email обязателен и уникален.
