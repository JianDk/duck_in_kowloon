from django.urls import path
from .rest_api import ContactSubmissionView
from .views import (
    ContactView,
)

urlpatterns = [
    path("contact/", ContactView.as_view(), name="contact"),
    path("api/contact/", ContactSubmissionView.as_view(), name="contact-submit"),
]