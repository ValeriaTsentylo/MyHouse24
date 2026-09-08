from django.urls import path

from .views import AdminDashboardView, UsersDashboardView

urlpatterns = [
    path("admin_dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("users_dashboard/", UsersDashboardView.as_view(), name="users_dashboard"),
]
