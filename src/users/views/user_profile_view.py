from django.views.generic import TemplateView
from src.users.models import User
from src.core.mixins import ResidentRequiredMixin


class UserProfileView(ResidentRequiredMixin, TemplateView):
    template_name = "users/admin/profile_staff_user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = User.objects.get(id=self.kwargs["user_id"])
        return context
