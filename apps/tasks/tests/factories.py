import factory

from apps.tasks.models import Comment, Task
from apps.users.tests.factories import UserFactory


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Задача {n}")
    description = "Описание задачи"
    status = Task.Status.TODO
    priority = Task.Priority.MEDIUM
    author = factory.SubFactory(UserFactory)
    assignee = None


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    task = factory.SubFactory(TaskFactory)
    author = factory.SubFactory(UserFactory)
    text = factory.Sequence(lambda n: f"Комментарий {n}")
