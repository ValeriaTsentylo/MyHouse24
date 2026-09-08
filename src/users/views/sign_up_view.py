import logging

from django.urls import reverse_lazy
from django.http import JsonResponse
from allauth.account.views import SignupView
from django.contrib.auth import get_user_model
from src.users.utils import verify_recaptcha
from allauth.account.utils import send_email_confirmation


# TODO: Розібратися чому не зберігає ПІБ для звичайного користувача. Також додати шоб роль зберігалася для нього, як користувач
logger = logging.getLogger(__name__)


class CustomSignupView(SignupView):
    template_name = "users/register_page.html"
    success_url = reverse_lazy("account_login")

    # def form_valid(self, form):
    #     email = form.cleaned_data.get("email")
    #     users = get_user_model()
    #
    #     if users.objects.filter(email=email).exists():
    #         form.add_error("email", "User with this email already exists.")
    #         return self.form_invalid(form)
    #
    #     recaptcha_response = self.request.POST.get("g-recaptcha-response")
    #     if verify_recaptcha(recaptcha_response):
    #         user = form.save(self.request)
    #         user.status = "new"
    #         user.is_active = False
    #         user.save()
    #
    #         send_email_confirmation(self.request, user)
    #
    #         return JsonResponse({"redirect_url": str(self.get_success_url())})
    #     else:
    #         form.add_error("g-recaptcha-response", "reCAPTCHA is not valid")
    #         return self.form_invalid(form)

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        users = get_user_model()

        if users.objects.filter(email=email).exists():
            form.add_error("email", "User with this email already exists.")
            return self.form_invalid(form)

        recaptcha_response = self.request.POST.get("g-recaptcha-response")
        if verify_recaptcha(recaptcha_response):
            user = form.save(
                self.request
            )  # Зберігає користувача, включаючи поле "name"
            user.status = "new"
            user.is_active = False
            user.save(
                update_fields=["status", "is_active"]
            )  # Уникає перезапису інших полів

            send_email_confirmation(self.request, user)

            return JsonResponse({"redirect_url": str(self.get_success_url())})
        else:
            form.add_error("g-recaptcha-response", "reCAPTCHA is not valid")
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.warning("Form errors: %s", form.errors)
        return JsonResponse({"errors": form.errors}, status=400)
