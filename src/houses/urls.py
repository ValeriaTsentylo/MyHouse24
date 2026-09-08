from django.urls import path

from .views import (
    CreateHouseView,
    DeleteHouseView,
    EditHouseView,
    HouseProfileView,
    HousesAjaxDatatableView,
    HousesListView,
)

urlpatterns = [
    path("create/", CreateHouseView.as_view(), name="house-create"),
    path("", HousesListView.as_view(), name="houses"),
    path(
        "houses/houses/datatable/",
        HousesAjaxDatatableView.as_view(),
        name="houses-datatable",
    ),
    path(
        "houses/profile-house/<int:house_id>/",
        HouseProfileView.as_view(),
        name="house-profile",
    ),
    path(
        "<int:pk>/delete/",
        DeleteHouseView.as_view(),
        name="houses-delete",
    ),
    path(
        "<int:pk>/edit/",
        EditHouseView.as_view(),
        name="house-edit",
    ),
]
