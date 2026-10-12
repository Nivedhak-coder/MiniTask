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
    remind_before = models.PositiveIntegerField(default=0)
    repeat = models.CharField(max_length=10, default="none", choices=[
    ("none", "Does not repeat"), ("daily", "Repeat daily"),
    ("weekdays", "Repeat on weekdays"), ("weekly", "Repeat weekly")])
    spawned = models.BooleanField(default=False)
    remind_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    skin = models.CharField(max_length=7, default="#e0ac69")
    hair = models.CharField(max_length=7, default="#2b1b12")
    eyes = models.CharField(max_length=7, default="#111111")
    lips = models.CharField(max_length=7, default="#d9777f")
    accent = models.CharField("Accessory color", max_length=7, default="#7657ff")
    face = models.CharField(max_length=8, default="oval", choices=[
        ("oval", "Oval"), ("round", "Round"), ("square", "Square")])
    eye_style = models.CharField(max_length=8, default="round", choices=[
        ("round", "Round"), ("big", "Big"), ("narrow", "Narrow")])
    outfit_style = models.CharField(max_length=8, default="tee", choices=[
        ("tee", "T-shirt"), ("hoodie", "Hoodie"), ("collar", "Collared shirt")])
    accessory = models.CharField(max_length=10, default="none", choices=[
        ("none", "None"), ("cap", "Cap"), ("headband", "Headband"),
        ("headphones", "Headphones"), ("earrings", "Earrings")])
    outfit = models.CharField(max_length=7, default="#7657ff")
    hair_style = models.CharField(max_length=10, default="short", choices=[
        ("short", "Short"), ("long", "Long"), ("bun", "Bun"),
        ("curly", "Curly"), ("bald", "Bald"), ("bob", "Bob"),
        ("ponytail", "Ponytail"), ("afro", "Afro"), ("spiky", "Spiky")])
    glasses = models.BooleanField(default=False)
    beard = models.BooleanField(default=False)
    token = models.CharField(max_length=64, blank=True, db_index=True)
    tone = models.CharField(max_length=10, default="friendly", choices=[
        ("friendly", "Friendly"), ("strict", "Strict"), ("funny", "Funny")])