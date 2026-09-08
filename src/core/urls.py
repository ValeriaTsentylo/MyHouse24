from django.urls import path

from src.core import views

urlpatterns = [
    path("", views.index, name="index"),
]
