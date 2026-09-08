from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from src.core.mixins import StaffRequiredMixin
from src.service.forms.tariff_form import ServicePriceFormSet, TariffForm
from src.service.models import Service, Tariff


class EditTariffView(StaffRequiredMixin, View):
    template_name = "tariff/edit_tariff_page.html"
    success_url = "tariffs"

    def get(self, request, pk):
        tariff = get_object_or_404(Tariff, pk=pk)
        tariff_form = TariffForm(instance=tariff)
        service_price_formset = ServicePriceFormSet(instance=tariff, prefix="service_price")
        services = Service.objects.select_related("unit_of_change").all()

        return render(
            request,
            self.template_name,
            {
                "tariff_form": tariff_form,
                "service_price_formset": service_price_formset,
                "services": services,
                "tariff": tariff,
            },
        )

    def post(self, request, pk):
        tariff = get_object_or_404(Tariff, pk=pk)
        tariff_form = TariffForm(request.POST, instance=tariff)
        service_price_formset = ServicePriceFormSet(
            request.POST, instance=tariff, prefix="service_price"
        )

        if tariff_form.is_valid() and service_price_formset.is_valid():
            tariff_form.save()
            service_price_formset.save()

            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {
                "tariff_form": tariff_form,
                "service_price_formset": service_price_formset,
                "tariff": tariff,
            },
        )
