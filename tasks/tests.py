from django.contrib.auth.models import User
from django.test import TestCase

from .models import Task


class TaskModelTest(TestCase):

    def test_task_creation(self):
        user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        task = Task.objects.create(
            user=user,
            title="Learn Django"
        )

        self.assertEqual(task.title, "Learn Django")
        self.assertFalse(task.completed)


class TaskSecurityTest(TestCase):

    def test_task_belongs_to_user(self):
        user1 = User.objects.create_user(
            username="user1",
            password="password123"
        )

        user2 = User.objects.create_user(
            username="user2",
            password="password123"
        )

        task = Task.objects.create(
            user=user1,
            title="Private task"
        )

        self.assertEqual(task.user, user1)
        self.assertNotEqual(task.user, user2)