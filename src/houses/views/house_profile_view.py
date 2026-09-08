from django.views.generic import TemplateView

from src.core.mixins import StaffRequiredMixin
from src.houses.models import Floor, House, Section


class HouseProfileView(StaffRequiredMixin, TemplateView):
    template_name = "houses/house_profile_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        house = House.objects.get(id=self.kwargs["house_id"])
        context["house"] = house
        context["sections_count"] = Section.objects.filter(house=house).count()
        context["floors_count"] = Floor.objects.filter(house=house).count()
        context["staff"] = house.staff.select_related("user").all()
        return context
