from django.shortcuts import redirect, render
from django.views import View

from src.core.mixins import StaffRequiredMixin
from src.service.forms.tariff_form import ServicePriceFormSet, TariffForm
from src.service.models import Service


class AddTariffView(StaffRequiredMixin, View):
    template_name = "tariff/add_tariff_page.html"

    success_url = "tariffs"

    def get(self, request):
        tariff_form = TariffForm()
        service_price_formset = ServicePriceFormSet(prefix="service_price")
        services = Service.objects.select_related("unit_of_change").all()

        return render(
            request,
            self.template_name,
            {
                "tariff_form": tariff_form,
                "service_price_formset": service_price_formset,
                "services": services,
            },
        )

    def post(self, request):
        tariff_form = TariffForm(request.POST)
        service_price_formset = ServicePriceFormSet(request.POST, prefix="service_price")

        if tariff_form.is_valid() and service_price_formset.is_valid():
            tariff_instance = tariff_form.save()

            service_price_instances = service_price_formset.save(commit=False)
            for service_price in service_price_instances:
                if service_price.service is None:
                    continue

                service_price.tariff = tariff_instance
                service_price.save()

            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {
                "tariff_form": tariff_form,
                "service_price_formset": service_price_formset,
            },
        )
