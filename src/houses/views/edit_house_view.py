from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

from src.houses.forms.edit_house_form import EditHouseForm
from src.houses.forms.floor_form import FloorFormSet
from src.houses.forms.section_form import SectionFormSet
from src.houses.forms.staff_form import StaffFormSet
from src.houses.models import House
from src.core.mixins import StaffRequiredMixin


class EditHouseView(StaffRequiredMixin, UpdateView):
    model = House
    template_name = "houses/edit_house_page.html"
    form_class = EditHouseForm
    success_url = reverse_lazy("houses")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        house = self.object

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

    def form_valid(self, form):
        context = self.get_context_data()
        section_formset = context["section_formset"]
        floor_formset = context["floor_formset"]
        staff_formset = context["staff_formset"]

        if (
            section_formset.is_valid()
            and floor_formset.is_valid()
            and staff_formset.is_valid()
        ):
            try:
                with transaction.atomic():
                    house = form.save()
                    section_formset.instance = house
                    floor_formset.instance = house
                    staff_formset.instance = house

                    section_formset.save()

                    floor_formset.save()

                    staff_formset.save()

                return redirect(self.success_url)
            except Exception as e:
                form.add_error(None, f"Помилка збереження: {e}")
                return self.render_to_response(self.get_context_data(form=form))
        else:
            form.add_error(None, "Перевірте помилки у формсеті.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        section_formset = context["section_formset"]
        floor_formset = context["floor_formset"]
        staff_formset = context["staff_formset"]

        context["section_formset_errors"] = section_formset.errors
        context["floor_formset_errors"] = floor_formset.errors
        context["staff_formset_errors"] = staff_formset.errors

        return self.render_to_response(context)
