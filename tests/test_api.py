"""API tests for MentorMatch (Django REST Framework)."""
import pytest
from django.utils import timezone

from matcher.models import Mentor, Mentee, MentorshipMatch, Session


@pytest.mark.django_db
class TestMentorApi:
    def test_create_and_list_mentors(self, client):
        resp = client.post("/api/mentors/", {
            "name": "Ava", "email": "ava@api.com",
            "skills": "Python, Django", "interests": "chess",
        }, content_type="application/json")
        assert resp.status_code == 201
        resp = client.get("/api/mentors/")
        assert resp.status_code == 200
        assert any(m["name"] == "Ava" for m in resp.json())

    def test_create_mentor_requires_name(self, client):
        resp = client.post("/api/mentors/", {"email": "x@x.com"},
                           content_type="application/json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestMatchesApi:
    def test_compute_matches_ranks_and_persists(self, client):
        mentor = Mentor.objects.create(name="Ava", email="ava@m.com",
                                       skills="Python, Django",
                                       interests="chess", availability="evenings")
        Mentor.objects.create(name="Zed", email="zed@m.com", skills="Rust")
        mentee = Mentee.objects.create(name="Ben", email="ben@m.com",
                                       skills="python", interests="chess",
                                       availability="evenings")
        resp = client.get(f"/api/mentees/{mentee.pk}/matches/")
        assert resp.status_code == 200
        payload = resp.json()
        assert len(payload) == 2
        assert payload[0]["mentor"]["name"] == "Ava"
        assert payload[0]["score"] > payload[1]["score"]
        assert payload[0]["shared_skills"] == ["python"]
        # persisted with explainable breakdown
        match = MentorshipMatch.objects.get(pk=payload[0]["match_id"])
        assert match.explanation["shared_skills"] == ["python"]

    def test_compute_matches_is_idempotent(self, client):
        mentor = Mentor.objects.create(name="Ava", email="ava2@m.com", skills="Python")
        mentee = Mentee.objects.create(name="Ben", email="ben2@m.com", skills="python")
        url = f"/api/mentees/{mentee.pk}/matches/"
        client.get(url)
        client.get(url)
        assert MentorshipMatch.objects.filter(mentor=mentor, mentee=mentee).count() == 1


@pytest.mark.django_db
class TestSessionsApi:
    def _match(self):
        mentor = Mentor.objects.create(name="Ava", email="ava3@m.com")
        mentee = Mentee.objects.create(name="Ben", email="ben3@m.com")
        return MentorshipMatch.objects.create(mentor=mentor, mentee=mentee, score=80.0)

    def test_propose_and_accept_session(self, client):
        match = self._match()
        resp = client.post("/api/sessions/", {
            "match": match.pk,
            "proposed_by": "mentee",
            "scheduled_at": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
            "topic": "Career chat",
        }, content_type="application/json")
        assert resp.status_code == 201
        assert resp.json()["status"] == "proposed"

        resp = client.post(f"/api/sessions/{resp.json()['id']}/accept/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "accepted"

    def test_cannot_accept_twice(self, client):
        match = self._match()
        session = Session.objects.create(
            match=match, proposed_by="mentor",
            scheduled_at=timezone.now() + timezone.timedelta(days=1))
        client.post(f"/api/sessions/{session.pk}/accept/")
        resp = client.post(f"/api/sessions/{session.pk}/accept/")
        assert resp.status_code == 400

    def test_decline_session(self, client):
        match = self._match()
        session = Session.objects.create(
            match=match, proposed_by="mentee",
            scheduled_at=timezone.now() + timezone.timedelta(days=1))
        resp = client.post(f"/api/sessions/{session.pk}/decline/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "declined"
