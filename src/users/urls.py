from django.urls import include, path

from .views import (
    CreateStaffUserView,
    CustomLoginView,
    CustomSignupView,
    DeleteUserView,
    EditStaffUserView,
    UserProfileView,
    UsersStaffAjaxDatatableView,
    UsersStaffListView,
)

urlpatterns = [
    path("accounts/signup/", CustomSignupView.as_view(), name="register"),
    path("accounts/login/", CustomLoginView.as_view(), name="account_login"),
    path("accounts/", include("allauth.urls")),
    path("users-staff/", UsersStaffListView.as_view(), name="users-staff"),
    path(
        "users/users-staff/datatable/",
        UsersStaffAjaxDatatableView.as_view(),
        name="users-staff-datatable",
    ),
    path("users-staff/create/", CreateStaffUserView.as_view(), name="users-staff-create"),
    path(
        "users-staff/<int:pk>/edit/",
        EditStaffUserView.as_view(),
        name="users-staff-edit",
    ),
    path(
        "users-staff/<int:pk>/delete/",
        DeleteUserView.as_view(),
        name="users-staff-delete",
    ),
    path(
        "users-staff/profile-staff-user/<int:user_id>/",
        UserProfileView.as_view(),
        name="user-staff-profile",
    ),
]
