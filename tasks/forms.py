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
    remind_before = forms.TypedChoiceField(
        coerce=int, initial=0,
        choices=[(0, "Remind at due time"), (5, "Remind 5 min before"),
                 (10, "Remind 10 min before"), (30, "Remind 30 min before"),
                 (60, "Remind 1 hour before")],
    )

    class Meta:
        model = Task
        fields = ["title", "due_at", "remind_before", "repeat"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter a task..."}
            )
        }

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["skin", "hair", "eyes", "lips", "outfit", "hair_style", "glasses", "beard", "tone"]
        widgets = {f: forms.TextInput(attrs={"type": "color"}) for f in ["skin", "hair", "eyes", "lips", "outfit"]}