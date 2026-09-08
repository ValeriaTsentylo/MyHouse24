from allauth.account.views import LoginView
from django.contrib.auth import login
from django.http import JsonResponse
from django.urls import reverse_lazy

from src.users.forms.login_form import CustomLoginForm
from src.users.utils import is_email_verified, verify_recaptcha


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "users/login_page.html"
    success_url_admin = reverse_lazy("admin_dashboard")
    success_url_user = reverse_lazy("users_dashboard")

    def form_valid(self, form):
        recaptcha_response = self.request.POST.get("g-recaptcha-response")
        role = self.request.POST.get("role")

        if verify_recaptcha(recaptcha_response):
            user = form.user

            if user:
                if not is_email_verified(user):
                    form.add_error(None, "Please verify your email address")
                    return self.form_invalid(form)

                # Перевірка ролі користувача
                if role == "admin" and user.is_staff:
                    login(self.request, user)
                    return JsonResponse({"redirect_url": str(self.success_url_admin)}, status=200)
                elif role == "resident" and not user.is_staff:
                    login(self.request, user)
                    return JsonResponse({"redirect_url": str(self.success_url_user)}, status=200)
                else:
                    form.add_error(None, "User role mismatch. Please check your credentials.")
                    return self.form_invalid(form)
            else:
                form.add_error(None, "Invalid email or password")
                return self.form_invalid(form)
        else:
            form.add_error("g-recaptcha-response", "reCAPTCHA is not valid")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return JsonResponse({"errors": form.errors}, status=400)
