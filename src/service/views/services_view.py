from django.shortcuts import redirect, render
from django.views import View

from src.core.mixins import StaffRequiredMixin
from src.service.forms.service_form import ServiceFormSet, UnitFormSet
from src.service.models import Service, UnitOfChange


class ServicesView(StaffRequiredMixin, View):
    template_name = "service/service_page.html"
    success_url = "services"

    def get(self, request):
        unit_formset = UnitFormSet(queryset=UnitOfChange.objects.all())
        service_formset = ServiceFormSet(queryset=Service.objects.all(), prefix="service")

        units = UnitOfChange.objects.values("id", "name")

        return render(
            request,
            self.template_name,
            {
                "unit_formset": unit_formset,
                "service_formset": service_formset,
                "units": list(units),
            },
        )

    def post(self, request):
        unit_formset = UnitFormSet(request.POST, queryset=UnitOfChange.objects.all())
        service_formset = ServiceFormSet(
            request.POST, queryset=Service.objects.all(), prefix="service"
        )

        if unit_formset.is_valid() and service_formset.is_valid():
            unit_instances = unit_formset.save()

            service_instances = service_formset.save()

            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {
                "unit_formset": unit_formset,
                "service_formset": service_formset,
            },
        )
