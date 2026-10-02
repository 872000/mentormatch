"""MentorMatch data model: mentors, mentees, matches and sessions."""
from django.core.validators import MinValueValidator
from django.db import models


class Mentor(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    # Comma-separated tags, e.g. "Python, Django, Career advice"
    skills = models.CharField(max_length=500, blank=True,
                              help_text="Comma-separated skills, e.g. Python, Django")
    interests = models.CharField(max_length=500, blank=True,
                                 help_text="Comma-separated interests")
    availability = models.CharField(
        max_length=200, blank=True,
        help_text="e.g. Weekday evenings, Saturday mornings")
    max_mentees = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (mentor)"


class Mentee(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=500, blank=True,
                              help_text="Comma-separated skills you want to grow")
    interests = models.CharField(max_length=500, blank=True,
                                 help_text="Comma-separated interests")
    availability = models.CharField(max_length=200, blank=True)
    goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (mentee)"


class MentorshipMatch(models.Model):
    """A persisted scoring of one mentor for one mentee."""

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="matches")
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE, related_name="matches")
    score = models.FloatField()
    # Explainable breakdown, e.g. {"shared_skills": [...], "components": {...}}
    explanation = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["mentor", "mentee"], name="unique_mentor_mentee")
        ]
        ordering = ["-score"]

    def __str__(self):
        return f"{self.mentor.name} x {self.mentee.name} ({self.score:.1f})"


class Session(models.Model):
    """A proposed/accepted mentorship meeting attached to a match."""

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class ProposedBy(models.TextChoices):
        MENTOR = "mentor", "Mentor"
        MENTEE = "mentee", "Mentee"

    match = models.ForeignKey(MentorshipMatch, on_delete=models.CASCADE, related_name="sessions")
    proposed_by = models.CharField(max_length=10, choices=ProposedBy.choices)
    scheduled_at = models.DateTimeField()
    topic = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"Session: {self.match} @ {self.scheduled_at:%Y-%m-%d %H:%M}"
