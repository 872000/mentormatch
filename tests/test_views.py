"""Server-rendered UI tests for MentorMatch."""
import pytest
from django.urls import reverse
from django.utils import timezone

from matcher.models import Mentor, Mentee, MentorshipMatch, Session


@pytest.mark.django_db
class TestUi:
    def test_index_loads(self, client):
        resp = client.get(reverse("matcher:index"))
        assert resp.status_code == 200
        assert b"MentorMatch" in resp.content

    def test_mentee_detail_shows_ranked_matches(self, client):
        mentor = Mentor.objects.create(name="Ava", email="ava@u.com",
                                       skills="Python", interests="chess")
        mentee = Mentee.objects.create(name="Ben", email="ben@u.com",
                                       skills="python", interests="chess")
        resp = client.get(reverse("matcher:mentee_detail", args=[mentee.pk]))
        assert resp.status_code == 200
        assert b"Ava" in resp.content
        assert b"Shared skills" in resp.content

    def test_create_mentor_form(self, client):
        resp = client.post(reverse("matcher:mentor_create"), {
            "name": "Cara", "email": "cara@u.com",
            "skills": "Go", "interests": "running", "max_mentees": 2,
        })
        assert resp.status_code == 302
        assert Mentor.objects.filter(name="Cara").exists()

    def test_create_mentee_form(self, client):
        resp = client.post(reverse("matcher:mentee_create"), {
            "name": "Dan", "email": "dan@u.com",
            "skills": "React", "interests": "music",
        })
        assert resp.status_code == 302
        assert Mentee.objects.filter(name="Dan").exists()

    def test_session_list_shows_upcoming(self, client):
        mentor = Mentor.objects.create(name="Ava", email="ava2@u.com")
        mentee = Mentee.objects.create(name="Ben", email="ben2@u.com")
        match = MentorshipMatch.objects.create(mentor=mentor, mentee=mentee, score=70.0)
        Session.objects.create(match=match, proposed_by="mentor",
                               scheduled_at=timezone.now() + timezone.timedelta(days=3),
                               topic="Intro call")
        resp = client.get(reverse("matcher:session_list"))
        assert resp.status_code == 200
        assert b"Intro call" in resp.content

    def test_accept_session_from_ui(self, client):
        mentor = Mentor.objects.create(name="Ava", email="ava3@u.com")
        mentee = Mentee.objects.create(name="Ben", email="ben3@u.com")
        match = MentorshipMatch.objects.create(mentor=mentor, mentee=mentee, score=70.0)
        session = Session.objects.create(
            match=match, proposed_by="mentee",
            scheduled_at=timezone.now() + timezone.timedelta(days=3))
        resp = client.get(reverse("matcher:session_accept", args=[session.pk]))
        assert resp.status_code == 302
        session.refresh_from_db()
        assert session.status == Session.Status.ACCEPTED

    def test_propose_session_form_creates_session(self, client):
        mentor = Mentor.objects.create(name="Ava", email="ava4@u.com")
        mentee = Mentee.objects.create(name="Ben", email="ben4@u.com")
        match = MentorshipMatch.objects.create(mentor=mentor, mentee=mentee, score=70.0)
        future = (timezone.now() + timezone.timedelta(days=5)).strftime("%Y-%m-%dT%H:%M")
        resp = client.post(reverse("matcher:session_propose", args=[match.pk]), {
            "proposed_by": "mentor", "scheduled_at": future, "topic": "Deep dive",
        })
        assert resp.status_code == 302
        assert Session.objects.filter(match=match, topic="Deep dive").exists()
