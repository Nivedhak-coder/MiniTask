from datetime import timedelta

from django.utils import timezone

from .models import Task


def bell(request):
    if not request.user.is_authenticated:
        return {}
    now = timezone.now()
    items = list(Task.objects.filter(
        user=request.user, completed=False, due_at__isnull=False,
        due_at__lte=now + timedelta(hours=24),
    ).order_by("due_at")[:6])
    for t in items:
        t.overdue = t.due_at < now
    return {"bell_tasks": items, "bell_count": len(items)}