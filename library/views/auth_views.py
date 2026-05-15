"""
Autentifikatsiya view'lari — RegisterView, LoginView, LogoutView.
Requirements: 1.1–1.7, 2.1–2.3, 2.5, 2.6
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views import View

from library.forms import RegistrationForm, LoginForm
from library.services.auth_service import AuthService, AuthServiceError


class RegisterView(View):
    """
    Ro'yxatdan o'tish view'i.
    GET  /auth/register/ — formani ko'rsatadi
    POST /auth/register/ — formani qayta ishlaydi
    Requirement 1.1–1.7
    """

    template_name = 'auth/register.html'

    def get(self, request):
        # Allaqachon kirgan foydalanuvchini bosh sahifaga yo'naltirish
        if request.user.is_authenticated:
            return redirect('/')
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('/')

        form = RegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                AuthService.register(
                    first_name=cd['first_name'],
                    last_name=cd['last_name'],
                    email=cd['email'],
                    phone_number=cd['phone_number'],
                    password=cd['password'],
                )
                messages.success(
                    request,
                    "Ro'yxatdan muvaffaqiyatli o'tdingiz! Endi tizimga kirishingiz mumkin."
                )
                return redirect('/auth/login/')
            except ValidationError as e:
                # AuthService'dan kelgan validatsiya xatolari
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field if field in form.fields else None, error)
                else:
                    messages.error(request, str(e.message))

        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """
    Kirish view'i.
    GET  /auth/login/ — formani ko'rsatadi
    POST /auth/login/ — autentifikatsiya qiladi
    Requirement 2.1–2.3
    """

    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('/')

        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                AuthService.login(
                    request,
                    phone_number=cd['phone_number'],
                    password=cd['password'],
                )
                # next parametri bo'lsa, u yerga yo'naltirish
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            except AuthServiceError as e:
                # Requirement 2.3: qaysi maydon noto'g'ri ekanini ko'rsatmaslik
                messages.error(request, str(e))

        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """
    Chiqish view'i.
    POST /auth/logout/ — sessiyani tugatadi va login sahifasiga yo'naltiradi
    Requirement 2.5
    """

    def post(self, request):
        AuthService.logout(request)
        messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
        return redirect('/auth/login/')

    # GET so'rovini ham qo'llab-quvvatlash (navbar logout tugmasi uchun)
    def get(self, request):
        AuthService.logout(request)
        return redirect('/auth/login/')
