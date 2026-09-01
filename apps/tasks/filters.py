from django_filters import rest_framework as filters

from apps.tasks.models import Task


class TaskFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Task.Status.choices)
    priority = filters.ChoiceFilter(choices=Task.Priority.choices)
    assignee = filters.NumberFilter(field_name="assignee_id")
    author = filters.NumberFilter(field_name="author_id")
    is_assigned = filters.BooleanFilter(field_name="assignee", lookup_expr="isnull", exclude=True)
    due_before = filters.IsoDateTimeFilter(field_name="due_date", lookup_expr="lte")
    due_after = filters.IsoDateTimeFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = ["status", "priority", "assignee", "author", "is_assigned"]
