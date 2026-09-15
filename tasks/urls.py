from django.urls import path

from . import views


urlpatterns = [
    path("", views.task_list, name="tasks"),
    path(
        "complete/<int:task_id>/",
        views.complete_task,
        name="complete_task"
    ),
    path(
        "delete/<int:task_id>/",
        views.delete_task,
        name="delete_task"
    ),
]