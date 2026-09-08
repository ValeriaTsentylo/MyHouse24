from src.users.models import User
from src.roles.models import RolePermission


from ajax_datatable import AjaxDatatableView
from django.views.generic import TemplateView
from django.urls import reverse
from src.core.mixins import StaffRequiredMixin


class UsersStaffListView(StaffRequiredMixin, TemplateView):
    template_name = "users/admin/users_table_staff.html"


# TODO: Додати логіку для відправлення листа
class UsersStaffAjaxDatatableView(StaffRequiredMixin, AjaxDatatableView):
    model = User
    title = "Користувачі"
    initial_order = [["id", "asc"]]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, "Всі"]]

    status_choices = [[key, label] for key, label in User.STATUS_CHOICES]
    role_choices = [[key, label] for key, label in RolePermission.ROLE_CHOICES]

    column_defs = [
        {"name": "id", "title": "#", "visible": True, "searchable": False},
        {"name": "name", "title": "ПІБ", "visible": True, "orderable": False},
        {
            "name": "role__name",
            "title": "Роль",
            "visible": True,
            "orderable": False,
            "searchable": True,
            "choices": role_choices,
        },
        {"name": "phone", "title": "Телефон", "visible": True, "orderable": False},
        {"name": "email", "visible": True, "orderable": False},
        {
            "name": "status",
            "title": "Статус",
            "visible": True,
            "orderable": False,
            "searchable": True,
            "choices": status_choices,
        },
        {
            "name": "actions",
            "title": " ",
            "searchable": False,
            "orderable": False,
            "visible": True,
        },
    ]

    def customize_row(self, row, obj):
        row["DT_RowAttr"] = {"data-id": obj.id}

        status_map = {"new": "Новий", "active": "Активний", "disabled": "Неактивний"}

        status_class_map = {
            "new": "status-new",
            "active": "status-active",
            "disabled": "status-disabled",
        }

        row["role__name"] = obj.role.get_display_name() if obj.role else "Без ролі"
        row["status"] = (
            f'<span class="status-badge {status_class_map.get(obj.status, "status-new")}">{status_map.get(obj.status, obj.status)}</span>'
        )
        row["actions"] = """
            <div style="display: inline-flex; gap: 3px;">
                <a href="#" class="btn btn-default btn-xs" title="Відправити запрошення"><i class="fas fa-sync-alt"></i></a>
                <a href="{}" class="btn btn-default btn-xs" title="Редагувати"><i class="fas fa-edit"></i></a>
                <button type="button" class="btn btn-default btn-xs delete-user-btn" title="Видалити" data-url="{}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        """.format(
            reverse("users-staff-edit", kwargs={"pk": obj.pk}),
            reverse("users-staff-delete", kwargs={"pk": obj.pk}),
        )


# TODO: Видалити цей метод, якщо він не потрібен
# def get(self, request, *args, **kwargs):
#     if "draw" not in request.GET:
#         request.GET = request.GET.copy()
#         request.GET["draw"] = "1"
#     try:
#         return super().get(request, *args, **kwargs)
#     except MultiValueDictKeyError as e:
#         missing_key = e.args[0]
#         return JsonResponse({"error": f"Missing parameter: {missing_key}"})
