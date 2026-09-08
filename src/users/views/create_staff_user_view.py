from django.db import transaction
from django.shortcuts import redirect, render
from django.views.generic import View

from src.core.mixins import StaffRequiredMixin
from src.roles.models import RolePermission
from src.users.forms.create_staff_user_form import CreateStaffUserForm
from src.users.models import User
from src.users.tasks import send_email_task


class CreateStaffUserView(StaffRequiredMixin, View):
    template_name = "users/admin/create_staff_user.html"
    form_class = CreateStaffUserForm

    def get(self, request):
        form = self.form_class()
        roles = RolePermission.objects.all()

        status_choices = User.STATUS_CHOICES

        return render(
            request,
            self.template_name,
            {"form": form, "roles": roles, "status_choices": status_choices},
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password1"]

            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(password)
                user.is_staff = True
                user.role = form.cleaned_data["role"]
                user.save()

            # Підготовка даних для листа
            subject = "Ваш обліковий запис адміністратора створено"
            context = {
                "admin_user_name": user.name,
                "roles": user.role.name,
                "password": password,
            }

            # Викликаємо завдання Celery для асинхронної відправки листа
            transaction.on_commit(
                lambda: send_email_task.delay(
                    subject, "emails_template/account_create.html", context, user.email
                )
            )

            return redirect("users-staff")
        else:
            roles = RolePermission.objects.all()
            status_choices = User.STATUS_CHOICES
            return render(
                request,
                self.template_name,
                {"form": form, "roles": roles, "status_choices": status_choices},
            )
