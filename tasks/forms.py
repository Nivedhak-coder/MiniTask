from django import forms
from .models import Task, Profile


class TaskForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Task
        fields = ["title", "due_at"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter a task..."}
            )
        }

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["skin", "hair", "eyes", "outfit", "hair_style", "glasses", "beard", "tone"]
        widgets = {f: forms.TextInput(attrs={"type": "color"}) for f in ["skin", "hair", "eyes", "outfit"]}