from ajax_datatable import AjaxDatatableView
from django.urls import reverse
from django.views.generic import TemplateView

from src.service.models import Account
from src.core.mixins import StaffRequiredMixin


class AccountsListView(StaffRequiredMixin, TemplateView):
    template_name = "account/accounts_datatable.html"


class AccountsAjaxDatatableView(StaffRequiredMixin, AjaxDatatableView):
    model = Account
    title = "Статті прихід/розхід"
    initial_order = [["name", "asc"]]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, "Всі"]]

    column_defs = [
        {"name": "id", "title": "#", "visible": False, "searchable": False},
        {
            "name": "name",
            "title": "Назва",
            "visible": True,
            "orderable": True,
            "searchable": False,
        },
        {
            "name": "type",
            "title": "Прихід/Розхід",
            "visible": True,
            "orderable": False,
            "searchable": False,
        },
        {
            "name": "actions",
            "title": "Дії",
            "visible": True,
            "orderable": False,
            "searchable": False,
        },
    ]

    def customize_row(self, row, obj):
        if obj.type == "income":
            color_class = "text-success"
        elif obj.type == "expenses":
            color_class = "text-danger"
        else:
            color_class = "text-muted"

        row["type"] = f'<span class="{color_class}">{obj.get_type_display()}</span>'

        row["actions"] = """
            <div style="display: inline-flex; gap: 3px;">
                <a href="{}" class="btn btn-default btn-xs" title="Редагувати"><i class="fas fa-edit"></i></a>
                <button type="button" class="btn btn-default btn-xs delete-user-btn" title="Видалити" data-url="{}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        """.format(
            reverse("edit-account", kwargs={"pk": obj.pk}),
            reverse("delete-account", kwargs={"pk": obj.pk}),
        )
