from django.urls import path

from .views import (
    ApartmentProfileView,
    ApartmentsAjaxDatatableView,
    ApartmentsListView,
    CreateApartmentView,
    DeleteApartmentView,
    EditApartmentView,
    GetSectionsAndFloorsView,
)

urlpatterns = [
    path("create/", CreateApartmentView.as_view(), name="apartment-create"),
    path(
        "get-sections-and-floors/",
        GetSectionsAndFloorsView.as_view(),
        name="get_sections_and_floors",
    ),
    path("", ApartmentsListView.as_view(), name="apartments"),
    path(
        "apartments/apartments/datatable/",
        ApartmentsAjaxDatatableView.as_view(),
        name="apartments-datatable",
    ),
    path(
        "<int:pk>/delete/",
        DeleteApartmentView.as_view(),
        name="apartment-delete",
    ),
    path(
        "apartment-profile/<int:apartment_id>/",
        ApartmentProfileView.as_view(),
        name="apartment-profile",
    ),
    path("apartments/<int:pk>/edit/", EditApartmentView.as_view(), name="edit_apartment"),
]
