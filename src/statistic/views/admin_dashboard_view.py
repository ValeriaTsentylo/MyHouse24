from django.views.generic import TemplateView
from src.core.mixins import StaffRequiredMixin


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "statistic/admin_dashboard.html"
