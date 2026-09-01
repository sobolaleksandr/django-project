from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tasks.models import Task
from apps.tasks.tests.factories import CommentFactory, TaskFactory

pytestmark = pytest.mark.django_db


def test_task_str():
    task = TaskFactory(title="Написать тесты")

    assert str(task) == "Написать тесты"


def test_comment_str():
    comment = CommentFactory(text="Короткий комментарий")

    assert "Короткий комментарий" in str(comment)


def test_mark_completed_sets_status_and_timestamp():
    task = TaskFactory()

    task.mark_completed()
    task.refresh_from_db()

    assert task.status == Task.Status.DONE
    assert task.completed_at is not None
    assert task.is_completed is True


def test_mark_completed_is_idempotent():
    task = TaskFactory()
    task.mark_completed()
    first_completed_at = task.completed_at

    task.mark_completed()
    task.refresh_from_db()

    assert task.completed_at == first_completed_at


def test_reopen_clears_completion():
    task = TaskFactory()
    task.mark_completed()

    task.reopen()
    task.refresh_from_db()

    assert task.status == Task.Status.IN_PROGRESS
    assert task.completed_at is None


def test_reopen_does_nothing_for_active_task():
    task = TaskFactory(status=Task.Status.TODO)

    task.reopen()
    task.refresh_from_db()

    assert task.status == Task.Status.TODO


def test_is_overdue():
    overdue = TaskFactory(due_date=timezone.now() - timedelta(days=1))
    upcoming = TaskFactory(due_date=timezone.now() + timedelta(days=1))

    assert overdue.is_overdue is True
    assert upcoming.is_overdue is False


def test_completed_task_is_not_overdue():
    task = TaskFactory(due_date=timezone.now() - timedelta(days=1))
    task.mark_completed()

    assert task.is_overdue is False


def test_deleting_task_removes_comments():
    comment = CommentFactory()
    task = comment.task

    task.delete()

    assert not type(comment).objects.filter(pk=comment.pk).exists()


def test_deleting_assignee_keeps_task():
    task = TaskFactory(assignee=TaskFactory().author)

    task.assignee.delete()
    task.refresh_from_db()

    assert task.assignee is None
