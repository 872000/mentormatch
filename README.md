# MentorMatch

![MentorMatch banner](docs/banner.png)

A mentorship matching platform: mentors and mentees build profiles (skills,
interests, availability), an explainable scoring engine ranks the best mentor
for every mentee, and pairs can propose/accept session times — all through a
server-rendered UI plus a Django REST Framework API.

## Features

- **Profiles** — mentors & mentees with skills, interests, availability, bios, goals
- **Explainable matching algorithm** — every pair scores 0–100 from
  skill coverage (60%), interest similarity (30%), and availability overlap (10%);
  each score ships with a breakdown of shared skills, shared interests, and the
  per-component math, so nobody wonders *why* they were matched
- **Session scheduling** — propose times on a match, accept/decline them,
  upcoming-sessions list
- **REST API** — full CRUD for mentors, mentees, matches, sessions, plus
  `GET /api/mentees/<id>/matches/` which ranks every mentor, persists the
  scored matches, and returns the explainable payload
- **Server-rendered UI** — home dashboard, mentor/mentee lists & detail pages
  with match-explanation cards, session proposal forms, accept/decline buttons
- **100% offline** — SQLite, no API keys, no network calls

## How to run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 — the browsable API lives at http://127.0.0.1:8000/api/.

## How to test

```bash
pytest
```

## Tech stack

Python · Django · Django REST Framework · SQLite · pytest / pytest-django
