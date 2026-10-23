"""The MentorMatch scoring engine.

Every pair gets a 0-100 score built from explainable components:

  score = 100 * (0.6 * skill_coverage + 0.3 * interest_similarity + 0.1 * availability_bonus)

- skill_coverage: fraction of the *mentor's* skills that also appear in the
  mentee's skill list — can this mentor teach what the mentee wants to learn?
- interest_similarity: Jaccard similarity of interest tags — shared passions
  make pairings stick.
- availability_bonus: 1.0 when mentor and mentee share at least one
  availability token, else 0.0 — a meeting has to happen sometime.

Tags are normalized (trimmed, lower-cased) so "Python" matches "python".
"""
from __future__ import annotations

SKILL_WEIGHT = 0.6
INTEREST_WEIGHT = 0.3
AVAILABILITY_WEIGHT = 0.1


def normalize_tags(raw: str) -> set[str]:
    """Split a comma-separated tag string into a normalized set."""
    if not raw:
        return set()
    return {part.strip().lower() for part in raw.split(",") if part.strip()}


def score_pair(mentor_skills: str, mentor_interests: str, mentor_availability: str,
               mentee_skills: str, mentee_interests: str, mentee_availability: str) -> dict:
    """Score one mentor/mentee pair, returning score + explainable breakdown."""
    m_skills = normalize_tags(mentor_skills)
    e_skills = normalize_tags(mentee_skills)
    shared_skills = sorted(m_skills & e_skills)
    skill_coverage = len(shared_skills) / len(m_skills) if m_skills else 0.0

    m_interests = normalize_tags(mentor_interests)
    e_interests = normalize_tags(mentee_interests)
    shared_interests = sorted(m_interests & e_interests)
    union = m_interests | e_interests
    interest_similarity = len(shared_interests) / len(union) if union else 0.0

    m_avail = normalize_tags(mentor_availability)
    e_avail = normalize_tags(mentee_availability)
    overlap = sorted(m_avail & e_avail)
    availability_bonus = 1.0 if overlap else 0.0

    components = {
        "skill_coverage": round(skill_coverage, 3),
        "interest_similarity": round(interest_similarity, 3),
        "availability_bonus": availability_bonus,
        "weights": {"skills": SKILL_WEIGHT, "interests": INTEREST_WEIGHT,
                    "availability": AVAILABILITY_WEIGHT},
    }
    score = round(
        100 * (SKILL_WEIGHT * skill_coverage
               + INTEREST_WEIGHT * interest_similarity
               + AVAILABILITY_WEIGHT * availability_bonus),
        1,
    )
    return {
        "score": score,
        "shared_skills": shared_skills,
        "shared_interests": shared_interests,
        "shared_availability": overlap,
        "components": components,
    }


def rank_mentors_for(mentee, mentors) -> list[dict]:
    """Rank an iterable of Mentor objects for a mentee, best first."""
    ranked = []
    for mentor in mentors:
        result = score_pair(
            mentor.skills, mentor.interests, mentor.availability,
            mentee.skills, mentee.interests, mentee.availability,
        )
        ranked.append({"mentor": mentor, **result})
    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked
