"""Model tests for MentorMatch."""
import pytest
from django.db import IntegrityError

from matcher.models import Mentor, Mentee, MentorshipMatch, Session


@pytest.mark.django_db
class TestModels:
    def test_mentor_str(self):
        m = Mentor.objects.create(name="Ava", email="ava@x.com")
        assert str(m) == "Ava (mentor)"

    def test_mentee_str(self):
        m = Mentee.objects.create(name="Ben", email="ben@x.com")
        assert str(m) == "Ben (mentee)"

    def test_mentor_defaults(self):
        m = Mentor.objects.create(name="Ava", email="ava2@x.com")
        assert m.max_mentees == 3

    def test_match_unique_per_pair(self):
        mentor = Mentor.objects.create(name="A", email="a@x.com")
        mentee = Mentee.objects.create(name="B", email="b@x.com")
        MentorshipMatch.objects.create(mentor=mentor, mentee=mentee, score=50.0)
        with pytest.raises(IntegrityError):
            MentorshipMatch.objects.create(mentor=mentor, mentee=mentee, score=60.0)

    def test_match_orders_by_score_desc(self):
        mentor = Mentor.objects.create(name="A", email="a2@x.com")
        low = Mentee.objects.create(name="L", email="l@x.com")
        high = Mentee.objects.create(name="H", email="h@x.com")
        MentorshipMatch.objects.create(mentor=mentor, mentee=low, score=10.0)
        MentorshipMatch.objects.create(mentor=mentor, mentee=high, score=90.0)
        scores = [m.score for m in MentorshipMatch.objects.all()]
        assert scores == [90.0, 10.0]

    def test_session_defaults_to_proposed(self):
        mentor = Mentor.objects.create(name="A", email="a3@x.com")
        mentee = Mentee.objects.create(name="B", email="b3@x.com")
        match = MentorshipMatch.objects.create(mentor=mentor, mentee=mentee, score=75.0)
        from django.utils import timezone
        s = Session.objects.create(match=match, proposed_by="mentee",
                                   scheduled_at=timezone.now())
        assert s.status == Session.Status.PROPOSED
        assert "Session" in str(s)
