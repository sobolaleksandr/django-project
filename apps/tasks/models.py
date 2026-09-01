from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "К выполнению"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Выполнена"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"

    title = models.CharField("название", max_length=200)
    description = models.TextField("описание", blank=True)
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        db_index=True,
    )
    priority = models.CharField(
        "приоритет",
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="автор",
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="исполнитель",
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )
    due_date = models.DateTimeField("срок выполнения", null=True, blank=True)
    completed_at = models.DateTimeField("дата выполнения", null=True, blank=True)
    created_at = models.DateTimeField("создана", auto_now_add=True)
    updated_at = models.DateTimeField("обновлена", auto_now=True)

    class Meta:
        verbose_name = "задача"
        verbose_name_plural = "задачи"
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["status", "assignee"])]

    def __str__(self) -> str:
        return self.title

    @property
    def is_completed(self) -> bool:
        return self.status == self.Status.DONE

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_date and not self.is_completed and self.due_date < timezone.now())

    def mark_completed(self) -> None:
        if self.is_completed:
            return
        self.status = self.Status.DONE
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def reopen(self) -> None:
        if not self.is_completed:
            return
        self.status = self.Status.IN_PROGRESS
        self.completed_at = None
        self.save(update_fields=["status", "completed_at", "updated_at"])


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        verbose_name="задача",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="автор",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField("текст")
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("обновлён", auto_now=True)

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"{self.author}: {self.text[:50]}"
