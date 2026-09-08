import logging

from django.views.generic import View
from django.shortcuts import render, redirect
from src.users.forms.edit_staff_user_form import EditStaffUserForm
from src.users.models import User
from src.roles.models import RolePermission
from src.users.tasks import send_email_task
from src.core.mixins import StaffRequiredMixin


logger = logging.getLogger(__name__)


class EditStaffUserView(StaffRequiredMixin, View):
    template_name = "users/admin/edit_staff_user.html"
    form_class = EditStaffUserForm

    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        form = self.form_class(instance=user)
        roles = RolePermission.objects.all()
        status_choices = User.STATUS_CHOICES
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "user": user,
                "roles": roles,
                "status_choices": status_choices,
            },
        )

    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        form = self.form_class(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password1")

            if password:
                user.set_password(password)

            user.is_staff = True
            user.save()

            role = form.cleaned_data["role"]
            user.role = role
            user.save()

            subject = "Ваш обліковий запис адміністратора відредаговано"
            context = {
                "admin_user_name": user.name,
                "roles": user.role.name,
                "password": password if password else "Ваш пароль не було змінено.",
            }

            try:
                send_email_task.delay(
                    subject, "emails_template/account_change.html", context, user.email
                )
            except Exception as e:
                logger.warning(f"Failed to send email: {e}")

            return redirect("users-staff")
        else:
            roles = RolePermission.objects.all()
            status_choices = User.STATUS_CHOICES
            return render(
                request,
                self.template_name,
                {"form": form, "roles": roles, "status_choices": status_choices},
            )
