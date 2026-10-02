"""Unit tests for the MentorMatch scoring engine."""
import pytest

from matcher import matching
from matcher.models import Mentor, Mentee


@pytest.mark.django_db
class TestNormalizeTags:
    def test_splits_and_lowercases(self):
        assert matching.normalize_tags("Python, Django,  React") == {"python", "django", "react"}

    def test_empty_string_gives_empty_set(self):
        assert matching.normalize_tags("") == set()

    def test_none_gives_empty_set(self):
        assert matching.normalize_tags(None) == set()

    def test_deduplicates(self):
        assert matching.normalize_tags("python, Python, PYTHON") == {"python"}


@pytest.mark.django_db
class TestScorePair:
    def test_perfect_match_scores_100(self):
        result = matching.score_pair(
            "Python, Django", "hiking, chess", "weekends",
            "python, django", "hiking, chess", "weekends",
        )
        assert result["score"] == 100.0
        assert result["shared_skills"] == ["django", "python"]
        assert result["shared_interests"] == ["chess", "hiking"]

    def test_no_overlap_scores_zero(self):
        result = matching.score_pair(
            "Rust", "golf", "mondays",
            "Python", "chess", "tuesdays",
        )
        assert result["score"] == 0.0

    def test_skills_weighted_more_than_interests(self):
        skills_only = matching.score_pair(
            "Python", "golf", "mondays", "python", "chess", "tuesdays")
        interests_only = matching.score_pair(
            "Rust", "chess", "mondays", "Python", "chess", "tuesdays")
        assert skills_only["score"] > interests_only["score"]

    def test_explanation_breaks_down_components(self):
        result = matching.score_pair(
            "Python, Java", "chess", "evenings",
            "python", "chess", "evenings")
        comps = result["components"]
        assert comps["skill_coverage"] == 0.5          # 1 of 2 mentor skills
        assert comps["interest_similarity"] == 1.0
        assert comps["availability_bonus"] == 1.0
        assert result["score"] == pytest.approx(70.0)  # 0.6*0.5 + 0.3*1.0 + 0.1*1.0

    def test_availability_overlap_adds_bonus(self):
        with_overlap = matching.score_pair("Rust", "golf", "Evenings",
                                           "Python", "chess", "evenings")
        without_overlap = matching.score_pair("Rust", "golf", "Mornings",
                                              "Python", "chess", "evenings")
        assert with_overlap["score"] == 10.0
        assert without_overlap["score"] == 0.0

    def test_empty_mentor_profile_does_not_crash(self):
        result = matching.score_pair("", "", "", "Python", "chess", "evenings")
        assert result["score"] == 0.0


@pytest.mark.django_db
class TestRankMentors:
    def test_ranks_best_first(self):
        mentee = Mentee.objects.create(name="E", email="e@x.com",
                                       skills="python", interests="chess")
        best = Mentor.objects.create(name="Best", email="b@x.com",
                                     skills="Python, Django", interests="chess, hiking")
        worst = Mentor.objects.create(name="Worst", email="w@x.com",
                                      skills="Rust", interests="golf")
        ranked = matching.rank_mentors_for(mentee, Mentor.objects.all())
        assert [r["mentor"].pk for r in ranked] == [best.pk, worst.pk]
        assert ranked[0]["score"] > ranked[1]["score"]

    def test_no_mentors_gives_empty_list(self):
        mentee = Mentee.objects.create(name="E", email="e2@x.com")
        assert matching.rank_mentors_for(mentee, Mentor.objects.all()) == []
