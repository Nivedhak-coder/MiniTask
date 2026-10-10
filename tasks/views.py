import secrets
from datetime import timedelta
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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

        context = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "productivity": productivity,
            "todays_tasks": todays_tasks,
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


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect("tasks")
    else:
        form = TaskForm()

    return render(
        request,
        "tasks.html",
        {
            "tasks": tasks,
            "form": form,
        }
    )


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    task.completed = not task.completed
    task.save()

    return redirect("tasks")


@login_required
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
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    profile = (
        Profile.objects.filter(token=token).select_related("user").first()
        if token else None
    )
    if not profile:
        return JsonResponse({"error": "unauthorized"}, status=401)

    due = list(Task.objects.filter(
        user=profile.user, completed=False, reminded=False,
        due_at__isnull=False, due_at__lte=timezone.now(),
    ))
    Task.objects.filter(id__in=[t.id for t in due]).update(reminded=True)

    return JsonResponse({
        "username": profile.user.username,
        "avatar": {
            "skin": profile.skin, "hair": profile.hair, "eyes": profile.eyes,
            "outfit": profile.outfit, "hair_style": profile.hair_style,
            "glasses": profile.glasses, "beard": profile.beard,
            "tone": profile.tone,
        },
        "reminders": [
            {"id": t.id, "title": t.title,
            "due": timezone.localtime(t.due_at).strftime("%H:%M")}
            for t in due
        ],
    })

@csrf_exempt
def reminder_action(request, task_id, action):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    profile = Profile.objects.filter(token=token).select_related("user").first() if token else None
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
        task.due_at = timezone.now() + timedelta(minutes=10)
        task.reminded = False
    else:
        return JsonResponse({"error": "bad action"}, status=400)
    task.save()
    return JsonResponse({"ok": True})

