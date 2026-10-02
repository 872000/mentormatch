from rest_framework import serializers

from .models import Mentor, Mentee, MentorshipMatch, Session


class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentor
        fields = "__all__"


class MenteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentee
        fields = "__all__"


class MentorshipMatchSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source="mentor.name", read_only=True)
    mentee_name = serializers.CharField(source="mentee.name", read_only=True)

    class Meta:
        model = MentorshipMatch
        fields = "__all__"
        read_only_fields = ("score", "explanation")


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = "__all__"
        read_only_fields = ("status",)
