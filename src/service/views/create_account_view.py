from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from src.core.mixins import StaffRequiredMixin
from src.service.forms.account_form import AccountForm


class CreateAccountView(StaffRequiredMixin, FormView):
    template_name = "account/account.html"
    form_class = AccountForm

    success_url = reverse_lazy("accounts")

    def form_valid(self, form):
        form.save()

        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
