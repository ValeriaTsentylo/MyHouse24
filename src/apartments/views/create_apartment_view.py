from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView

from src.apartments.forms.create_apartment_form import CreateApartmentForm
from src.core.mixins import StaffRequiredMixin
from src.houses.models import Floor, Section


# TODO: Додати рахунок та тариф для зберігання
class CreateApartmentView(StaffRequiredMixin, FormView):
    template_name = "apartments/create_apartment_page.html"
    form_class = CreateApartmentForm
    success_url = reverse_lazy("apartments")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    # Додано логіку для коректного оновлення queryset
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        house_id = self.request.POST.get("house")
        if house_id:
            kwargs["initial"] = kwargs.get("initial", {})
            kwargs["initial"]["house"] = house_id
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class GetSectionsAndFloorsView(StaffRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        action = request.GET.get("action")
        house_id = request.GET.get("house_id")

        if action == "get_sections" and house_id:
            sections = Section.objects.filter(house_id=house_id).values("id", "name")
            return JsonResponse(list(sections), safe=False)

        if action == "get_floors" and house_id:
            floors = Floor.objects.filter(house_id=house_id).values("id", "number")
            return JsonResponse(list(floors), safe=False)

        return JsonResponse({"error": "Invalid action"}, status=400)
