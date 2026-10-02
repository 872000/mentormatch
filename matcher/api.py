"""Django REST Framework API for MentorMatch."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import matching
from .models import Mentor, Mentee, MentorshipMatch, Session
from .serializers import (
    MentorSerializer,
    MenteeSerializer,
    MentorshipMatchSerializer,
    SessionSerializer,
)


class MentorViewSet(viewsets.ModelViewSet):
    queryset = Mentor.objects.all().order_by("name")
    serializer_class = MentorSerializer


class MenteeViewSet(viewsets.ModelViewSet):
    queryset = Mentee.objects.all().order_by("name")
    serializer_class = MenteeSerializer

    @action(detail=True, methods=["get"])
    def matches(self, request, pk=None):
        """Rank every mentor for this mentee and persist the scored matches.

        Returns the ranked list with explainable scores.
        """
        mentee = self.get_object()
        ranked = matching.rank_mentors_for(mentee, Mentor.objects.all())
        payload = []
        for entry in ranked:
            mentor = entry["mentor"]
            match, _ = MentorshipMatch.objects.update_or_create(
                mentor=mentor,
                mentee=mentee,
                defaults={
                    "score": entry["score"],
                    "explanation": {
                        "shared_skills": entry["shared_skills"],
                        "shared_interests": entry["shared_interests"],
                        "shared_availability": entry["shared_availability"],
                        "components": entry["components"],
                    },
                },
            )
            payload.append(
                {
                    "match_id": match.id,
                    "mentor": MentorSerializer(mentor).data,
                    "score": entry["score"],
                    "shared_skills": entry["shared_skills"],
                    "shared_interests": entry["shared_interests"],
                    "shared_availability": entry["shared_availability"],
                    "components": entry["components"],
                }
            )
        return Response(payload)


class MentorshipMatchViewSet(viewsets.ModelViewSet):
    queryset = MentorshipMatch.objects.select_related("mentor", "mentee").all()
    serializer_class = MentorshipMatchSerializer
    http_method_names = ["get", "post", "patch", "delete"]


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.select_related("match__mentor", "match__mentee").all()
    serializer_class = SessionSerializer

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        session = self.get_object()
        if session.status != Session.Status.PROPOSED:
            return Response(
                {"detail": "Only proposed sessions can be accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.status = Session.Status.ACCEPTED
        session.save(update_fields=["status"])
        return Response(SessionSerializer(session).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        session = self.get_object()
        if session.status != Session.Status.PROPOSED:
            return Response(
                {"detail": "Only proposed sessions can be declined."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.status = Session.Status.DECLINED
        session.save(update_fields=["status"])
        return Response(SessionSerializer(session).data)
