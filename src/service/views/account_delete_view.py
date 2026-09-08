from django.http import JsonResponse
from django.views import View

from src.core.mixins import StaffRequiredMixin
from src.service.models import Account


class DeleteAccountView(StaffRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        Account.objects.get(pk=self.kwargs["pk"]).delete()
        return JsonResponse(status=200, data={"success": True})
