"""
AuthService — ro'yxatdan o'tish, kirish va sessiyani boshqaradi.
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 2.2, 2.3, 2.5
"""

import re
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError

from library.models import User


class AuthServiceError(Exception):
    """AuthService xatolari uchun asosiy exception."""
    pass


class AuthService:
    """
    Foydalanuvchi autentifikatsiyasini boshqaruvchi servis.
    """

    # ------------------------------------------------------------------ #
    #  Validatsiya yordamchi metodlari                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_email_format(email: str) -> None:
        """
        Email formatini tekshiradi.
        Requirement 1.7
        """
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Email formati noto'g'ri. Masalan: user@gmail.com")

    @staticmethod
    def _validate_password_length(password: str) -> None:
        """
        Parol uzunligini tekshiradi (minimal 8 belgi).
        Requirement 1.6
        """
        if len(password) < 8:
            raise ValidationError("Parol kamida 8 belgidan iborat bo'lishi kerak.")

    @staticmethod
    def _check_phone_unique(phone_number: str, exclude_user_id: int = None) -> None:
        """
        Telefon raqami tizimda mavjud emasligini tekshiradi.
        Requirement 1.3
        """
        qs = User.objects.filter(phone_number=phone_number)
        if exclude_user_id:
            qs = qs.exclude(pk=exclude_user_id)
        if qs.exists():
            raise ValidationError("Bu telefon raqami allaqachon ro'yxatdan o'tgan.")

    @staticmethod
    def _check_email_unique(email: str, exclude_user_id: int = None) -> None:
        """
        Email tizimda mavjud emasligini tekshiradi.
        Requirement 1.4
        """
        qs = User.objects.filter(email__iexact=email)
        if exclude_user_id:
            qs = qs.exclude(pk=exclude_user_id)
        if qs.exists():
            raise ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")

    # ------------------------------------------------------------------ #
    #  validate_registration_data                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_registration_data(data: dict) -> dict:
        """
        Ro'yxatdan o'tish ma'lumotlarini to'liq tekshiradi.
        Requirement 1.2, 1.3, 1.4, 1.6, 1.7

        :param data: {first_name, last_name, email, phone_number, password}
        :returns: tozalangan data dict
        :raises ValidationError: birinchi topilgan xato uchun
        """
        errors = {}

        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        for field in required_fields:
            if not data.get(field, '').strip():
                errors[field] = f"'{field}' maydoni to'ldirilishi shart."

        if errors:
            raise ValidationError(errors)

        # Email format
        try:
            AuthService._validate_email_format(data['email'])
        except ValidationError as e:
            errors['email'] = e.message

        # Parol uzunligi
        try:
            AuthService._validate_password_length(data['password'])
        except ValidationError as e:
            errors['password'] = e.message

        # Telefon noyobligi
        try:
            AuthService._check_phone_unique(data['phone_number'])
        except ValidationError as e:
            errors['phone_number'] = e.message

        # Email noyobligi
        try:
            AuthService._check_email_unique(data['email'])
        except ValidationError as e:
            errors.setdefault('email', e.message)

        if errors:
            raise ValidationError(errors)

        return {k: v.strip() for k, v in data.items()}

    # ------------------------------------------------------------------ #
    #  register                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def register(first_name: str, last_name: str, email: str,
                 phone_number: str, password: str) -> User:
        """
        Yangi foydalanuvchi yaratadi.
        Requirement 1.5

        :returns: yaratilgan User obyekti
        :raises ValidationError: validatsiya xatosi bo'lsa
        """
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone_number': phone_number,
            'password': password,
        }
        cleaned = AuthService.validate_registration_data(data)

        user = User.objects.create_user(
            phone_number=cleaned['phone_number'],
            password=cleaned['password'],
            first_name=cleaned['first_name'],
            last_name=cleaned['last_name'],
            email=cleaned['email'],
        )
        return user

    # ------------------------------------------------------------------ #
    #  login                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def login(request, phone_number: str, password: str) -> User:
        """
        Foydalanuvchini tizimga kiritadi va sessiya yaratadi.
        Requirement 2.2, 2.3

        :returns: autentifikatsiya qilingan User
        :raises AuthServiceError: noto'g'ri ma'lumotlar yoki faol bo'lmagan hisob
        """
        user = authenticate(request, username=phone_number, password=password)
        if user is None:
            raise AuthServiceError("Telefon raqami yoki parol noto'g'ri.")
        if not user.is_active:
            raise AuthServiceError("Hisobingiz faolsizlantirilgan. Administrator bilan bog'laning.")
        login(request, user)
        return user

    # ------------------------------------------------------------------ #
    #  logout                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def logout(request) -> None:
        """
        Foydalanuvchi sessiyasini tugatadi.
        Requirement 2.5
        """
        logout(request)
