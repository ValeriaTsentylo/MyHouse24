"""Reusable access-control mixins.

The project defines custom permissions on ``users.User.Meta.permissions`` and a
``User.has_permission()`` helper; these mixins are what actually enforce them on
class-based views.
"""

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class StaffRequiredMixin(AccessMixin):
    """Allow only authenticated staff members.

    Set ``required_permission`` on a view to additionally require one of the
    custom permissions declared on the ``User`` model, e.g.::

        class HousesListView(StaffRequiredMixin, TemplateView):
            required_permission = "view_houses"
    """

    required_permission: str | None = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        if not (user.is_staff or user.is_superuser):
            raise PermissionDenied("Staff access required.")

        if (
            self.required_permission
            and not user.is_superuser
            and not user.has_permission(self.required_permission)
        ):
            raise PermissionDenied(f"Missing permission: {self.required_permission}")

        return super().dispatch(request, *args, **kwargs)


class ResidentRequiredMixin(AccessMixin):
    """Allow any authenticated user (resident cabinet pages)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
