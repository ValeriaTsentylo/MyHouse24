from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from src.houses.forms.create_house_form import CreateHouseForm
from src.houses.forms.floor_form import FloorFormSet
from src.houses.forms.section_form import SectionFormSet
from src.houses.forms.staff_form import StaffFormSet
from src.houses.models import House
from src.core.mixins import StaffRequiredMixin


class CreateHouseView(StaffRequiredMixin, FormView):
    template_name = "houses/create_house_page.html"
    form_class = CreateHouseForm
    success_url = reverse_lazy("houses")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        house = self.get_house()

        if self.request.POST:
            context["section_formset"] = SectionFormSet(
                self.request.POST, instance=house
            )
            context["floor_formset"] = FloorFormSet(self.request.POST, instance=house)
            context["staff_formset"] = StaffFormSet(self.request.POST, instance=house)
        else:
            context["section_formset"] = SectionFormSet(instance=house)
            context["floor_formset"] = FloorFormSet(instance=house)
            context["staff_formset"] = StaffFormSet(instance=house)
        return context

    def get_house(self):
        house_id = self.kwargs.get("pk")
        if house_id:
            return get_object_or_404(House, pk=house_id)
        return None

    def form_valid(self, form):
        context = self.get_context_data()
        section_formset = context["section_formset"]
        floor_formset = context["floor_formset"]
        staff_formset = context["staff_formset"]

        if not (
            section_formset.is_valid()
            and floor_formset.is_valid()
            and staff_formset.is_valid()
        ):
            return self.render_to_response(context)

        with transaction.atomic():
            house = form.save()
            for formset in (section_formset, floor_formset, staff_formset):
                formset.instance = house
                formset.save()

        return redirect(self.success_url)
