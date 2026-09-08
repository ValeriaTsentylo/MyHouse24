from django.urls import path

from .views import (
    AccountsAjaxDatatableView,
    AccountsListView,
    AddTariffView,
    CreateAccountView,
    DeleteAccountView,
    DeleteTariffView,
    EditAccountView,
    EditTariffView,
    ServicesView,
    TariffDetailView,
    TariffListView,
    TariffsAjaxDatatableView,
)

urlpatterns = [
    path("services", ServicesView.as_view(), name="services"),
    path("add-new-tariff", AddTariffView.as_view(), name="add-new-tariff"),
    path("tariffs/<int:pk>/edit/", EditTariffView.as_view(), name="edit_tariff"),
    path("tariffs", TariffListView.as_view(), name="tariffs"),
    path(
        "houses/houses/datatable/",
        TariffsAjaxDatatableView.as_view(),
        name="tariffs-datatable",
    ),
    path("tariffs/<int:pk>", TariffDetailView.as_view(), name="tariff_profile"),
    path(
        "tariffs/<int:pk>/delete/",
        DeleteTariffView.as_view(),
        name="tariff-delete",
    ),
    path("create-account/", CreateAccountView.as_view(), name="create-account"),
    path("edit-account/<int:pk>/", EditAccountView.as_view(), name="edit-account"),
    path("accounts/", AccountsListView.as_view(), name="accounts"),
    path(
        "accounts/datatable/",
        AccountsAjaxDatatableView.as_view(),
        name="accounts-datatable",
    ),
    path("accounts/delete/<int:pk>/", DeleteAccountView.as_view(), name="delete-account"),
]
