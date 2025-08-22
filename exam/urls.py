from django.urls import path
from .views import azexam_page

urlpatterns = [
    path("", azexam_page, name="azexam"),
]
