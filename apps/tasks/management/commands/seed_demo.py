from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.tasks.models import Comment, Task

User = get_user_model()

DEMO_PASSWORD = "DemoPassw0rd!"

DEMO_USERS = [
    ("alice", "alice@example.com", "Алиса", "Смирнова"),
    ("bob", "bob@example.com", "Борис", "Кузнецов"),
    ("carol", "carol@example.com", "Карина", "Орлова"),
]

DEMO_TASKS = [
    {
        "title": "Настроить CI",
        "description": "Поднять пайплайн с линтером и тестами.",
        "status": Task.Status.IN_PROGRESS,
        "priority": Task.Priority.HIGH,
        "author": "alice",
        "assignee": "bob",
        "due_in_days": 3,
    },
    {
        "title": "Написать документацию к API",
        "description": "Описать эндпоинты и примеры запросов.",
        "status": Task.Status.TODO,
        "priority": Task.Priority.MEDIUM,
        "author": "bob",
        "assignee": "carol",
        "due_in_days": 7,
    },
    {
        "title": "Обновить зависимости",
        "description": "Проверить совместимость и прогнать тесты.",
        "status": Task.Status.DONE,
        "priority": Task.Priority.LOW,
        "author": "carol",
        "assignee": "alice",
        "due_in_days": -1,
    },
]

DEMO_COMMENTS = [
    ("Настроить CI", "bob", "Взял в работу, жду доступ к раннеру."),
    ("Настроить CI", "alice", "Доступ выдан, можно продолжать."),
    ("Написать документацию к API", "carol", "Начну после релиза."),
]


class Command(BaseCommand):
    help = "Наполняет базу демонстрационными пользователями, задачами и комментариями."

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        users = {}
        for username, email, first_name, last_name in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": first_name, "last_name": last_name},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save(update_fields=["password"])
            users[username] = user

        tasks = {}
        for item in DEMO_TASKS:
            task, _ = Task.objects.get_or_create(
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "status": item["status"],
                    "priority": item["priority"],
                    "author": users[item["author"]],
                    "assignee": users[item["assignee"]],
                    "due_date": timezone.now() + timedelta(days=item["due_in_days"]),
                    "completed_at": (
                        timezone.now() if item["status"] == Task.Status.DONE else None
                    ),
                },
            )
            tasks[item["title"]] = task

        for task_title, username, text in DEMO_COMMENTS:
            Comment.objects.get_or_create(
                task=tasks[task_title],
                author=users[username],
                text=text,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: {len(users)} пользователей, {len(tasks)} задач, "
                f"{len(DEMO_COMMENTS)} комментариев. Пароль всех пользователей: {DEMO_PASSWORD}"
            )
        )
