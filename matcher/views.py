"""Server-rendered UI views for MentorMatch."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from . import matching
from .forms import MentorForm, MenteeForm, SessionForm
from .models import Mentor, Mentee, MentorshipMatch, Session


def index(request):
    context = {
        "mentor_count": Mentor.objects.count(),
        "mentee_count": Mentee.objects.count(),
        "upcoming_sessions": Session.objects.filter(
            status__in=[Session.Status.PROPOSED, Session.Status.ACCEPTED],
            scheduled_at__gte=timezone.now(),
        ).select_related("match__mentor", "match__mentee")[:10],
    }
    return render(request, "matcher/index.html", context)


def mentor_list(request):
    return render(request, "matcher/mentor_list.html",
                  {"mentors": Mentor.objects.all().order_by("name")})


def mentor_detail(request, pk):
    mentor = get_object_or_404(Mentor, pk=pk)
    return render(request, "matcher/mentor_detail.html", {
        "mentor": mentor,
        "matches": mentor.matches.select_related("mentee").order_by("-score")[:10],
    })


def mentor_create(request):
    if request.method == "POST":
        form = MentorForm(request.POST)
        if form.is_valid():
            mentor = form.save()
            messages.success(request, f"Mentor {mentor.name} added.")
            return redirect("matcher:mentor_detail", pk=mentor.pk)
    else:
        form = MentorForm()
    return render(request, "matcher/form.html", {"form": form, "title": "Add mentor"})


def mentee_list(request):
    return render(request, "matcher/mentee_list.html",
                  {"mentees": Mentee.objects.all().order_by("name")})


def mentee_detail(request, pk):
    mentee = get_object_or_404(Mentee, pk=pk)
    ranked = matching.rank_mentors_for(mentee, Mentor.objects.all())
    return render(request, "matcher/mentee_detail.html",
                  {"mentee": mentee, "ranked": ranked[:10]})


def mentee_create(request):
    if request.method == "POST":
        form = MenteeForm(request.POST)
        if form.is_valid():
            mentee = form.save()
            messages.success(request, f"Mentee {mentee.name} added.")
            return redirect("matcher:mentee_detail", pk=mentee.pk)
    else:
        form = MenteeForm()
    return render(request, "matcher/form.html", {"form": form, "title": "Add mentee"})


def session_list(request):
    sessions = Session.objects.select_related("match__mentor", "match__mentee").all()
    upcoming = sessions.filter(
        status__in=[Session.Status.PROPOSED, Session.Status.ACCEPTED],
        scheduled_at__gte=timezone.now(),
    )
    past = sessions.exclude(pk__in=upcoming.values("pk"))
    return render(request, "matcher/session_list.html",
                  {"upcoming": upcoming, "past": past})


def session_propose(request, match_id):
    """Persist a computed match (if needed) and propose a session time on it."""
    match = get_object_or_404(MentorshipMatch, pk=match_id)
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.match = match
            session.save()
            messages.success(request, "Session proposed.")
            return redirect("matcher:session_list")
    else:
        form = SessionForm()
    return render(request, "matcher/form.html",
                  {"form": form, "title": f"Propose session: {match}"})


def session_accept(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.status == Session.Status.PROPOSED:
        session.status = Session.Status.ACCEPTED
        session.save(update_fields=["status"])
        messages.success(request, "Session accepted.")
    return redirect("matcher:session_list")


def session_decline(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.status == Session.Status.PROPOSED:
        session.status = Session.Status.DECLINED
        session.save(update_fields=["status"])
        messages.info(request, "Session declined.")
    return redirect("matcher:session_list")
