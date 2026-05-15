"""
Profile view'lari — foydalanuvchi profili ko'rish va tahrirlash.
Requirements: 7.1–7.5
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View

from library.decorators import login_required_redirect
from library.forms import ProfileUpdateForm
from library.services.profile_service import ProfileService
from library.services.borrow_service import BorrowService


@method_decorator(login_required_redirect, name='dispatch')
class ProfileView(View):
    """
    Foydalanuvchi profil sahifasi.
    GET /profile/
    Requirements: 7.1, 7.2, 7.5
    """

    template_name = 'profile/profile.html'

    def get(self, request):
        borrow_history = ProfileService.get_borrow_history(request.user)
        active_count = ProfileService.get_active_borrows_count(request.user)

        context = {
            'user': request.user,
            'borrow_history': borrow_history,
            'active_borrows_count': active_count,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required_redirect, name='dispatch')
class ProfileUpdateView(View):
    """
    Foydalanuvchi profil tahrirlash sahifasi.
    GET  /profile/edit/
    POST /profile/edit/
    Requirements: 7.3, 7.4
    """

    template_name = 'profile/edit.html'

    def get(self, request):
        form = ProfileUpdateForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            try:
                ProfileService.update_profile(
                    user=request.user,
                    data=form.cleaned_data,
                )
                messages.success(request, "Profil ma'lumotlari muvaffaqiyatli yangilandi.")
                return redirect('/profile/')
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field if field in form.fields else None, error)
                else:
                    messages.error(request, str(e.message))

        return render(request, self.template_name, {'form': form})
