"""
ProfileService — foydalanuvchi profili ma'lumotlarini boshqaradi.
Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import re
from django.core.exceptions import ValidationError

from library.models import User, Borrow


class ProfileService:
    """
    Foydalanuvchi profili ma'lumotlarini boshqaruvchi servis.
    """

    @staticmethod
    def get_profile(user: User) -> User:
        """
        Foydalanuvchi profil ma'lumotlarini qaytaradi.
        Requirement 7.1
        """
        return user

    @staticmethod
    def update_profile(user: User, data: dict) -> User:
        """
        Foydalanuvchi profil ma'lumotlarini yangilaydi.
        Requirements: 7.3, 7.4

        :param user: yangilanadigan foydalanuvchi
        :param data: {first_name, last_name, email}
        :returns: yangilangan User
        :raises ValidationError: validatsiya xatosi bo'lsa
        """
        errors = {}

        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()

        if not first_name:
            errors['first_name'] = "Ism maydoni to'ldirilishi shart."
        if not last_name:
            errors['last_name'] = "Familiya maydoni to'ldirilishi shart."
        if not email:
            errors['email'] = "Email maydoni to'ldirilishi shart."
        else:
            # Email format validatsiyasi — Requirement 7.4
            pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                errors['email'] = "Email formati noto'g'ri. Masalan: user@gmail.com"
            elif User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
                errors['email'] = "Bu email allaqachon ro'yxatdan o'tgan."

        if errors:
            raise ValidationError(errors)

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save(update_fields=['first_name', 'last_name', 'email'])

        return user

    @staticmethod
    def get_borrow_history(user: User):
        """
        Foydalanuvchining barcha ijara tarixini qaytaradi.
        Requirement 7.2
        """
        return Borrow.objects.filter(user=user).select_related(
            'book', 'book__category'
        ).order_by('-borrowed_at')

    @staticmethod
    def get_active_borrows_count(user: User) -> int:
        """
        Foydalanuvchining faol ijara sonini qaytaradi.
        Requirement 7.5
        """
        return Borrow.objects.filter(user=user, returned=False).count()
