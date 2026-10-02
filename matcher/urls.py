from django.urls import path

from . import views

app_name = "matcher"

urlpatterns = [
    path("", views.index, name="index"),
    path("mentors/", views.mentor_list, name="mentor_list"),
    path("mentors/add/", views.mentor_create, name="mentor_create"),
    path("mentors/<int:pk>/", views.mentor_detail, name="mentor_detail"),
    path("mentees/", views.mentee_list, name="mentee_list"),
    path("mentees/add/", views.mentee_create, name="mentee_create"),
    path("mentees/<int:pk>/", views.mentee_detail, name="mentee_detail"),
    path("sessions/", views.session_list, name="session_list"),
    path("matches/<int:match_id>/sessions/propose/", views.session_propose,
         name="session_propose"),
    path("sessions/<int:pk>/accept/", views.session_accept, name="session_accept"),
    path("sessions/<int:pk>/decline/", views.session_decline, name="session_decline"),
]
