from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def index(request):
    return render(request, "admin/adminlte_base.html")
