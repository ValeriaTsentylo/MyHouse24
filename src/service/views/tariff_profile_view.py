from django.views.generic import DetailView

from src.core.mixins import StaffRequiredMixin
from src.service.models import ServicePrice, Tariff


class TariffDetailView(StaffRequiredMixin, DetailView):
    model = Tariff
    template_name = "tariff/tariff_profile_page.html"
    context_object_name = "tariff"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_prices"] = ServicePrice.objects.filter(tariff=self.object)
        return context
