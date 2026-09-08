from django.views.generic import TemplateView

from src.core.mixins import ResidentRequiredMixin


class UsersDashboardView(ResidentRequiredMixin, TemplateView):
    template_name = "statistic/users_dashboard.html"
