from ajax_datatable import AjaxDatatableView
from django.urls import reverse
from django.views.generic import TemplateView

from src.core.mixins import StaffRequiredMixin
from src.houses.models import House


class HousesListView(StaffRequiredMixin, TemplateView):
    template_name = "houses/houses_table.html"


class HousesAjaxDatatableView(StaffRequiredMixin, AjaxDatatableView):
    model = House
    title = "Дома"
    initial_order = [["id", "asc"]]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, "Всі"]]

    column_defs = [
        {"name": "id", "title": "#", "visible": True, "searchable": False},
        {"name": "name", "title": "Назва", "visible": True, "orderable": False},
        {"name": "adress", "title": "Адреса", "visible": True, "orderable": False},
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
            reverse("house-edit", kwargs={"pk": obj.pk}),
            reverse("houses-delete", kwargs={"pk": obj.pk}),
        )
