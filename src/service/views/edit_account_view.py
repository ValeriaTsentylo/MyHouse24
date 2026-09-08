from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from src.core.mixins import StaffRequiredMixin
from src.service.forms.account_form import AccountForm
from src.service.models import Account


class EditAccountView(StaffRequiredMixin, FormView):
    template_name = "account/account.html"
    form_class = AccountForm
    success_url = reverse_lazy("accounts")

    def get_object(self):
        return get_object_or_404(Account, pk=self.kwargs.get("pk"))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_object()
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
