from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(null=True, blank=True)
    reminded = models.BooleanField(default=False)
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    skin = models.CharField(max_length=7, default="#e0ac69")
    hair = models.CharField(max_length=7, default="#2b1b12")
    eyes = models.CharField(max_length=7, default="#111111")
    outfit = models.CharField(max_length=7, default="#7657ff")
    hair_style = models.CharField(max_length=10, default="short", choices=[
        ("short", "Short"), ("long", "Long"), ("bun", "Bun"),
        ("curly", "Curly"), ("bald", "Bald")])
    glasses = models.BooleanField(default=False)
    beard = models.BooleanField(default=False)
    token = models.CharField(max_length=64, blank=True, db_index=True)
    tone = models.CharField(max_length=10, default="friendly", choices=[
        ("friendly", "Friendly"), ("strict", "Strict"), ("funny", "Funny")])