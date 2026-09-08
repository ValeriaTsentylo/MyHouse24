from django.http import JsonResponse
from django.views import View

from src.service.models import Tariff
from src.core.mixins import StaffRequiredMixin


class DeleteTariffView(StaffRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        Tariff.objects.get(pk=self.kwargs["pk"]).delete()
        return JsonResponse(status=200, data={"success": True})
