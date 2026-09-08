from .account_datatable_view import AccountsAjaxDatatableView, AccountsListView
from .account_delete_view import DeleteAccountView
from .add_tariff_view import AddTariffView
from .create_account_view import CreateAccountView
from .delete_tariff_view import DeleteTariffView
from .edit_account_view import EditAccountView
from .edit_tariff_view import EditTariffView
from .services_view import ServicesView
from .tariff_profile_view import TariffDetailView
from .tariffs_datatable_view import TariffListView, TariffsAjaxDatatableView

__all__ = [
    "ServicesView",
    "AddTariffView",
    "TariffListView",
    "TariffsAjaxDatatableView",
    "EditTariffView",
    "TariffDetailView",
    "DeleteTariffView",
    "CreateAccountView",
    "AccountsListView",
    "AccountsAjaxDatatableView",
    "EditAccountView",
    "DeleteAccountView",
]
