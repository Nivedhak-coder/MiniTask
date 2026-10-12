import secrets
from datetime import timedelta
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import AvatarForm, TaskForm
from .models import Profile, Task

def home(request):
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user)

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(completed=True).count()
        pending_tasks = tasks.filter(completed=False).count()

        productivity = 0
        if total_tasks > 0:
            productivity = round(
                (completed_tasks / total_tasks) * 100
            )

        today = timezone.localdate()

        todays_tasks = tasks.filter(
            created_at__date=today
        ).order_by("completed", "-created_at")[:5]

        open_due = tasks.filter(completed=False, due_at__isnull=False)
        now = timezone.now()
        overdue_count = open_due.filter(due_at__lt=now).count()
        due_today = open_due.filter(due_at__gte=now, due_at__date=today).count()
        p = Profile.objects.filter(user=request.user).first()
        avatar = avatar_data(p) if p else None
        context = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "productivity": productivity,
            "todays_tasks": todays_tasks,
            "overdue_count": overdue_count,
            "due_today": due_today,
            "avatar": avatar,
        }

        return render(request, "home.html", context)

    return render(request, "home.html")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tasks")

    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    from django.contrib.auth import authenticate

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("tasks")

        return render(
            request,
            "login.html",
            {"error": "Invalid username or password."}
        )

    return render(request, "login.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    q = request.GET.get("q", "").strip()
    if q:
        tasks = tasks.filter(title__icontains=q)

    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            if task.due_at:
                task.remind_at = task.due_at - timedelta(minutes=task.remind_before)
            task.save()
            return redirect("tasks")
    else:
        form = TaskForm()

    now = timezone.now()
    today = timezone.localdate()
    ld = lambda t: timezone.localtime(t.due_at).date()
    tasks = list(tasks.order_by("due_at", "-created_at"))
    open_ = [t for t in tasks if not t.completed]
    groups = [
        ("Overdue", [t for t in open_ if t.due_at and t.due_at < now]),
        ("Today", [t for t in open_ if t.due_at and t.due_at >= now and ld(t) == today]),
        ("Upcoming", [t for t in open_ if t.due_at and t.due_at >= now and ld(t) > today]),
        ("No due date", [t for t in open_ if not t.due_at]),
        ("Completed", sorted([t for t in tasks if t.completed],
                             key=lambda t: t.created_at, reverse=True)[:20]),
    ]
    return render(
        request,
        "tasks.html",
        {"groups": [g for g in groups if g[1]], "form": form, "q": q}
    )


@login_required
@require_POST
def complete_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    task.completed = not task.completed
    task.save()
    if task.completed:
        spawn_next(task)

    return redirect("tasks")


@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    task.delete()

    return redirect("tasks")

@login_required
def avatar_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.token:
        profile.token = secrets.token_urlsafe(32)
        profile.save()
    if request.method == "POST":
        form = AvatarForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("avatar")
    else:
        form = AvatarForm(instance=profile)
    return render(request, "avatar.html", {"form": form, "token": profile.token})

@login_required
def regenerate_token(request):
    if request.method == "POST":
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.token = secrets.token_urlsafe(32)
        profile.save()
    return redirect("avatar")


def reminders_api(request):
    profile = api_profile(request)
    if not profile:
        return JsonResponse({"error": "unauthorized"}, status=401)

    now = timezone.now()
    due = list(Task.objects.filter(
        Q(remind_at__lte=now) | Q(remind_at__isnull=True, due_at__lte=now),
        user=profile.user, completed=False, reminded=False, due_at__isnull=False,
    ))
    Task.objects.filter(id__in=[t.id for t in due]).update(reminded=True)

    return JsonResponse({
        "username": profile.user.username,
        "update": {"version": settings.COMPANION_VERSION, "url": settings.COMPANION_DOWNLOAD_URL},
        "avatar": {**avatar_data(profile), "tone": profile.tone},
        "reminders": [
            {"id": t.id, "title": t.title,
            "due": timezone.localtime(t.due_at).strftime("%H:%M"),
            "late": now - t.due_at > timedelta(minutes=10),
             "mins": int((t.due_at - now).total_seconds() // 60)}
            for t in due
        ],
    })

@csrf_exempt
def reminder_action(request, task_id, action):
    profile = api_profile(request)
    if not profile:
        return JsonResponse({"error": "unauthorized"}, status=401)
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    task = Task.objects.filter(id=task_id, user=profile.user).first()
    if not task:
        return JsonResponse({"error": "not found"}, status=404)
    if action == "done":
        task.completed = True
    elif action == "snooze":
        task.remind_at = timezone.now() + timedelta(minutes=10)
        task.reminded = False
    else:
        return JsonResponse({"error": "bad action"}, status=400)
    task.save()
    if action == "done":
        spawn_next(task)
    return JsonResponse({"ok": True})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            if {"due_at", "remind_before"} & set(form.changed_data):
                task.reminded = False
            task.remind_at = (
                task.due_at - timedelta(minutes=task.remind_before) if task.due_at else None
            )
            task.save()
            return redirect("tasks")
    else:
        form = TaskForm(instance=task)
    return render(request, "edit_task.html", {"form": form})

def next_due(task):
    now = timezone.now()
    d = task.due_at
    while True:
        d += timedelta(days=7 if task.repeat == "weekly" else 1)
        if task.repeat == "weekdays" and timezone.localtime(d).weekday() >= 5:
            continue
        if d > now:
            return d


def spawn_next(task):
    if task.repeat == "none" or not task.due_at or task.spawned:
        return
    due = next_due(task)
    Task.objects.create(
        user=task.user, title=task.title, due_at=due, repeat=task.repeat,
        remind_before=task.remind_before,
        remind_at=due - timedelta(minutes=task.remind_before),
    )
    task.spawned = True
    task.save(update_fields=["spawned"])

def api_profile(request):
    ip = (request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[-1].strip()
          or request.META.get("REMOTE_ADDR", ""))
    key = f"badkey:{ip}"
    if cache.get(key, 0) >= 20:
        return None
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    profile = Profile.objects.filter(token=token).select_related("user").first() if token else None
    if not profile:
        cache.add(key, 0, 600)
        try:
            cache.incr(key)
        except ValueError:
            pass
    return profile

AVATAR_FIELDS = ["skin", "hair", "eyes", "lips", "outfit", "accent", "hair_style", "face",
                 "eye_style", "outfit_style", "accessory", "glasses", "beard"]


def avatar_data(p):
    return {f: getattr(p, f) for f in AVATAR_FIELDS}