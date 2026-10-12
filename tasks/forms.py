import re

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
        fields = ["skin", "face", "eyes", "eye_style", "lips", "hair", "hair_style", "outfit",
                  "outfit_style", "accessory", "accent", "glasses", "beard", "tone"]
        widgets = {f: forms.TextInput(attrs={"type": "color"}) for f in ["skin", "hair", "eyes", "lips", "outfit", "accent"]}

    def clean(self):
        d = super().clean()
        for f in ("skin", "hair", "eyes", "lips", "outfit", "accent"):
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", d.get(f) or ""):
                self.add_error(f, "Pick a valid color.")
        return d