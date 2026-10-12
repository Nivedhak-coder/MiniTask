from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import Profile, Task
from .views import next_due


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

PLAIN = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(SECURE_SSL_REDIRECT=False, STORAGES=PLAIN)
class Base(TestCase):
    def setUp(self):
        cache.clear()
        self.u1 = User.objects.create_user("u1", password="pw12345!")
        self.u2 = User.objects.create_user("u2", password="pw12345!")
        self.p1 = Profile.objects.create(user=self.u1, token="key1")
        self.p2 = Profile.objects.create(user=self.u2, token="key2")

    def login(self, name="u1"):
        self.client.login(username=name, password="pw12345!")

    def task(self, user=None, minutes=-1, **kw):
        due = timezone.now() + timedelta(minutes=minutes)
        return Task.objects.create(user=user or self.u1, title="T", due_at=due, **kw)

    def api(self, key="key1"):
        return self.client.get("/tasks/api/reminders/", HTTP_AUTHORIZATION=f"Bearer {key}")


class ReminderApiTest(Base):
    def test_rejects_missing_and_wrong_key(self):
        self.assertEqual(self.client.get("/tasks/api/reminders/").status_code, 401)
        self.assertEqual(self.api("nope").status_code, 401)

    def test_due_task_returned_once(self):
        t = self.task()
        self.assertEqual([r["id"] for r in self.api().json()["reminders"]], [t.id])
        self.assertEqual(self.api().json()["reminders"], [])

    def test_not_due_or_completed_not_returned(self):
        self.task(minutes=60)
        self.task(completed=True)
        self.assertEqual(self.api().json()["reminders"], [])

    def test_remind_before_fires_early(self):
        t = self.task(minutes=30, remind_before=10,
                      remind_at=timezone.now() - timedelta(minutes=1))
        self.assertEqual(self.api().json()["reminders"][0]["id"], t.id)

    def test_only_own_tasks(self):
        self.task(user=self.u2)
        self.assertEqual(self.api().json()["reminders"], [])

    def test_wrong_keys_get_throttled(self):
        for _ in range(20):
            self.api("bad")
        self.assertEqual(self.api().status_code, 401)


class ReminderActionTest(Base):
    def act(self, t, action, key="key1", method="post"):
        return getattr(self.client, method)(
            f"/tasks/api/reminders/{t.id}/{action}/", HTTP_AUTHORIZATION=f"Bearer {key}")

    def test_done(self):
        t = self.task()
        self.assertEqual(self.act(t, "done").status_code, 200)
        t.refresh_from_db()
        self.assertTrue(t.completed)

    def test_snooze_moves_reminder_not_due_time(self):
        t = self.task(reminded=True)
        due = t.due_at
        self.act(t, "snooze")
        t.refresh_from_db()
        self.assertFalse(t.reminded)
        self.assertEqual(t.due_at, due)
        self.assertGreater(t.remind_at, timezone.now() + timedelta(minutes=9))

    def test_other_users_task_is_404(self):
        t = self.task(user=self.u2)
        self.assertEqual(self.act(t, "done").status_code, 404)

    def test_get_not_allowed_and_bad_key(self):
        t = self.task()
        self.assertEqual(self.act(t, "done", method="get").status_code, 405)
        self.assertEqual(self.act(t, "done", key="bad").status_code, 401)


class WebSecurityTest(Base):
    def test_login_required(self):
        r = self.client.get("/tasks/")
        self.assertRedirects(r, "/login/?next=/tasks/", fetch_redirect_response=False)

    def test_cannot_touch_other_users_task(self):
        t = self.task(user=self.u2)
        self.login()
        self.assertEqual(self.client.post(f"/tasks/complete/{t.id}/").status_code, 404)
        self.assertEqual(self.client.post(f"/tasks/delete/{t.id}/").status_code, 404)
        self.assertEqual(self.client.get(f"/tasks/edit/{t.id}/").status_code, 404)
        self.assertTrue(Task.objects.filter(id=t.id, completed=False).exists())

    def test_destructive_urls_need_post(self):
        t = self.task()
        self.login()
        for url in (f"/tasks/complete/{t.id}/", f"/tasks/delete/{t.id}/", "/logout/"):
            self.assertEqual(self.client.get(url).status_code, 405, url)
        self.assertTrue(Task.objects.filter(id=t.id, completed=False).exists())

    def test_add_task_sets_remind_at(self):
        self.login()
        due = (timezone.localtime() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
        self.client.post("/tasks/", {"title": "X", "due_at": due,
                                     "remind_before": 30, "repeat": "none"})
        t = Task.objects.get(title="X")
        self.assertEqual(t.due_at - t.remind_at, timedelta(minutes=30))


class PagesTest(Base):
    def test_pages_render(self):
        t = self.task()
        self.task(minutes=-90000)
        self.task(minutes=300, completed=True)
        self.assertEqual(self.client.get("/").status_code, 200)
        self.login()
        for url in ("/", "/tasks/", "/tasks/?q=T", "/tasks/avatar/", f"/tasks/edit/{t.id}/"):
            self.assertEqual(self.client.get(url).status_code, 200, url)


class RepeatTest(Base):
    def done(self, t):
        self.login()
        return self.client.post(f"/tasks/complete/{t.id}/")

    def test_daily_creates_one_next_task_even_after_undo(self):
        t = self.task(minutes=-5, repeat="daily")
        self.done(t)
        self.done(t)
        self.done(t)
        self.assertEqual(Task.objects.filter(title="T").count(), 2)

    def test_late_task_next_due_is_in_future(self):
        t = self.task(minutes=-3 * 24 * 60, repeat="daily")
        self.assertGreater(next_due(t), timezone.now())
        self.assertLessEqual(next_due(t), timezone.now() + timedelta(days=1))

    def test_weekdays_skips_weekend(self):
        d = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=3)
        while timezone.localtime(d).weekday() != 4:
            d += timedelta(days=1)
        t = Task(user=self.u1, title="T", due_at=d, repeat="weekdays")
        self.assertEqual(timezone.localtime(next_due(t)).weekday(), 0)