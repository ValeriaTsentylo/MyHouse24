from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from src.apartments.forms.create_apartment_form import CreateApartmentForm
from src.apartments.models import Apartment
from src.core.mixins import StaffRequiredMixin


class EditApartmentView(StaffRequiredMixin, FormView):
    template_name = "apartments/edit_apartment_page.html"
    form_class = CreateApartmentForm
    success_url = reverse_lazy("apartments")

    def get_object(self):
        # Завантажуємо об'єкт на основі `pk` з URL
        pk = self.kwargs.get("pk")
        return get_object_or_404(Apartment, pk=pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Додаємо об'єкт як instance у форму
        kwargs["instance"] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apartment"] = (
            self.get_object()
        )  # Передаємо об'єкт в контекст для шаблону
        return context

    def form_valid(self, form):
        # Зберігаємо зміни в об'єкті
        form.save()
        return redirect(self.success_url)

    def form_invalid(self, form):
        # У разі помилки повертаємо форму з помилками
        return self.render_to_response(self.get_context_data(form=form))
