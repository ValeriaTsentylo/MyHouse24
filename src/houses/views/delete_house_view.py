from django.http import JsonResponse
from django.views import View
from src.houses.models import House
from src.core.mixins import StaffRequiredMixin


class DeleteHouseView(StaffRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        House.objects.get(pk=self.kwargs["pk"]).delete()
        return JsonResponse(status=200, data={"success": True})
