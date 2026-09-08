from ajax_datatable import AjaxDatatableView
from django.urls import reverse
from django.views.generic import TemplateView

from src.service.models import Tariff
from src.core.mixins import StaffRequiredMixin


class TariffListView(StaffRequiredMixin, TemplateView):
    template_name = "tariff/tariffs_table.html"


class TariffsAjaxDatatableView(StaffRequiredMixin, AjaxDatatableView):
    model = Tariff
    title = "Тарифи"
    initial_order = [["name", "asc"]]
    options_dict = {
        "searching": False,  # Вимикає пошук
    }
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, "Всі"]]

    column_defs = [
        {"name": "id", "title": "#", "visible": False, "searchable": False},
        {
            "name": "name",
            "title": "Назва тарифу",
            "visible": True,
            "orderable": True,
            "searchable": False,
        },
        {
            "name": "description",
            "title": "Опис тарифу",
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
        row["DT_RowAttr"] = {"data-id": obj.id}

        row["actions"] = """
            <div style="display: inline-flex; gap: 3px;">
                <a href="{}" class="btn btn-default btn-xs" title="Редагувати"><i class="fas fa-edit"></i></a>
                <button type="button" class="btn btn-default btn-xs delete-house-btn" title="Видалити" data-url="{}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        """.format(
            reverse("edit_tariff", kwargs={"pk": obj.pk}),
            reverse("tariff-delete", kwargs={"pk": obj.pk}),
        )
