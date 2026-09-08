from django.http import JsonResponse
from django.views import View

from src.core.mixins import StaffRequiredMixin
from src.users.models import User


class DeleteUserView(StaffRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        User.objects.get(pk=self.kwargs["pk"]).delete()
        return JsonResponse(status=200, data={"success": True})
