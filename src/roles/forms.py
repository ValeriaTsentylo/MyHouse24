from django import forms

from .models import RolePermission


class RolePermissionForm(forms.ModelForm):
    class Meta:
        model = RolePermission
        fields = ["is_active"]

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        if instance.is_active:
            instance.permissions.add(instance.permission)
        else:
            instance.permissions.remove(instance.permission)
        return instance
