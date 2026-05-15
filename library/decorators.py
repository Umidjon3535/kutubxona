"""
Dekoratorlar — login_required_redirect va admin_required.
Requirements: 2.6, 8.5
"""

from functools import wraps

from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages


def login_required_redirect(view_func):
    """
    Autentifikatsiya qilinmagan foydalanuvchilarni login sahifasiga yo'naltiradi.
    Requirement 2.6, 6.5

    Django'ning standart @login_required(login_url='/auth/login/') ga o'xshash,
    lekin loyiha uchun maxsus sozlangan.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/auth/login/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """
    Faqat is_staff=True bo'lgan foydalanuvchilarga ruxsat beradi.
    - Autentifikatsiya qilinmagan → login sahifasiga redirect
    - Autentifikatsiya qilingan, lekin is_staff=False → 403 Forbidden + bosh sahifaga redirect
    Requirement 8.5
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/auth/login/?next={request.path}')
        if not request.user.is_staff:
            messages.error(request, "Bu sahifaga kirishga ruxsatingiz yo'q.")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper
