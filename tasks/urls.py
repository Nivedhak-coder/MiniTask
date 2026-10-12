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
    path("avatar/", views.avatar_view, name="avatar"),
    path("api/reminders/", views.reminders_api, name="reminders_api"),
    path("avatar/token/", views.regenerate_token, name="regenerate_token"),
    path("api/reminders/<int:task_id>/<str:action>/", views.reminder_action, name="reminder_action"),
        path("edit/<int:task_id>/", views.edit_task, name="edit_task"),
]