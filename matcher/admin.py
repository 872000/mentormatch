from django.contrib import admin

from .models import Mentor, Mentee, MentorshipMatch, Session

admin.site.register(Mentor)
admin.site.register(Mentee)
admin.site.register(MentorshipMatch)
admin.site.register(Session)
