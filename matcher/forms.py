from django import forms

from .models import Mentor, Mentee, Session


class MentorForm(forms.ModelForm):
    class Meta:
        model = Mentor
        fields = ["name", "email", "bio", "skills", "interests", "availability", "max_mentees"]


class MenteeForm(forms.ModelForm):
    class Meta:
        model = Mentee
        fields = ["name", "email", "bio", "skills", "interests", "availability", "goals"]


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["proposed_by", "scheduled_at", "topic", "notes"]
        widgets = {
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
