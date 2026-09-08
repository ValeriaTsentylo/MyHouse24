from ajax_datatable import AjaxDatatableView
from django.urls import reverse
from django.views.generic import TemplateView

from src.apartments.models import Apartment
from src.houses.models import House
from src.users.models import User
from src.core.mixins import StaffRequiredMixin


# TODO: Додати відображення для Залишку як буде вже готова система обліку
class ApartmentsListView(StaffRequiredMixin, TemplateView):
    template_name = "apartments/apartments_datatable.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["houses"] = House.objects.all()
        context["users"] = User.objects.all()
        return context


class ApartmentsAjaxDatatableView(StaffRequiredMixin, AjaxDatatableView):
    model = Apartment
    title = "Квартири"
    initial_order = [["number", "asc"]]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, "Всі"]]
    search_values_separator = "+"

    column_defs = [
        {
            "name": "id",
            "title": "ID",
            "visible": False,
            "orderable": True,
            "searchable": False,
        },
        {
            "name": "number",
            "title": "№ квартири",
            "visible": True,
            "orderable": True,
            "searchable": False,
        },
        {
            "name": "house__name",
            "title": "Дім",
            "visible": True,
            "orderable": False,
            "searchable": False,
            "foreign_field": "house__name",
        },
        {
            "name": "section__name",
            "title": "Секція",
            "visible": True,
            "orderable": False,
            "searchable": False,
            "foreign_field": "section__name",
        },
        {
            "name": "floor__number",
            "title": "Поверх",
            "visible": True,
            "orderable": False,
            "searchable": False,
            "foreign_field": "floor__number",
        },
        {
            "name": "owner",
            "title": "Власник",
            "visible": True,
            "orderable": False,
            "searchable": False,
        },
        {
            "name": "actions",
            "title": "Дії",
            "searchable": False,
            "orderable": True,
        },
    ]

    def get_initial_queryset(self, request=None):
        queryset = super().get_initial_queryset(request)
        house_id = self.request.GET.get("house_id")
        section_id = self.request.GET.get("section_id")
        floor_id = self.request.GET.get("floor_id")

        if house_id:
            queryset = queryset.filter(house_id=house_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        if floor_id:
            queryset = queryset.filter(floor_id=floor_id)

        return queryset

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
            reverse("edit_apartment", kwargs={"pk": obj.pk}),
            reverse("apartment-delete", kwargs={"pk": obj.pk}),
        )
