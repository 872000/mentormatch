from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()
router.register(r"mentors", api.MentorViewSet, basename="mentor")
router.register(r"mentees", api.MenteeViewSet, basename="mentee")
router.register(r"matches", api.MentorshipMatchViewSet, basename="match")
router.register(r"sessions", api.SessionViewSet, basename="session")

urlpatterns = router.urls
