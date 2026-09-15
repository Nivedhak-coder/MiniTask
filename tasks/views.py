from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TaskForm
from .models import Task


def home(request):
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