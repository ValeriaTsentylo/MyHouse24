from django.views.generic import TemplateView

from src.apartments.models import Apartment
from src.core.mixins import StaffRequiredMixin


class ApartmentProfileView(StaffRequiredMixin, TemplateView):
    template_name = "apartments/apartment_profile_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apartment = Apartment.objects.get(id=self.kwargs["apartment_id"])
        context["apartment"] = apartment

        return context
