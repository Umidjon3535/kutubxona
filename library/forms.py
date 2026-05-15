"""
Django forms — RegistrationForm, LoginForm, BookForm.
Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 2.1, 3.1
"""

import re
from django import forms
from django.core.exceptions import ValidationError

from library.models import User, Category


# ------------------------------------------------------------------ #
#  RegistrationForm                                                    #
# ------------------------------------------------------------------ #

class RegistrationForm(forms.Form):
    """
    Ro'yxatdan o'tish formasi.
    Requirement 1.1: first_name, last_name, email, phone_number, password
    """

    first_name = forms.CharField(
        max_length=150,
        label="Ism",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Ismingizni kiriting',
        }),
        error_messages={'required': "Ism maydoni to'ldirilishi shart."},
    )

    last_name = forms.CharField(
        max_length=150,
        label="Familiya",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Familiyangizni kiriting',
        }),
        error_messages={'required': "Familiya maydoni to'ldirilishi shart."},
    )

    email = forms.EmailField(
        max_length=254,
        label="Gmail manzili",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'example@gmail.com',
        }),
        error_messages={
            'required': "Email maydoni to'ldirilishi shart.",
            'invalid': "Email formati noto'g'ri. Masalan: user@gmail.com",
        },
    )

    phone_number = forms.CharField(
        max_length=20,
        label="Telefon raqami",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': '+998901234567',
        }),
        error_messages={'required': "Telefon raqami maydoni to'ldirilishi shart."},
    )

    password = forms.CharField(
        label="Parol",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Kamida 8 belgi',
        }),
        error_messages={
            'required': "Parol maydoni to'ldirilishi shart.",
            'min_length': "Parol kamida 8 belgidan iborat bo'lishi kerak.",
        },
    )

    password_confirm = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Parolni qayta kiriting',
        }),
        error_messages={'required': "Parolni tasdiqlash maydoni to'ldirilishi shart."},
    )

    # ---- field-level validations ---- #

    def clean_email(self):
        """
        Email format va noyobligini tekshiradi.
        Requirement 1.4, 1.7
        """
        email = self.cleaned_data.get('email', '').strip()
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Email formati noto'g'ri. Masalan: user@gmail.com")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def clean_phone_number(self):
        """
        Telefon raqami noyobligini tekshiradi.
        Requirement 1.3
        """
        phone = self.cleaned_data.get('phone_number', '').strip()
        if User.objects.filter(phone_number=phone).exists():
            raise ValidationError("Bu telefon raqami allaqachon ro'yxatdan o'tgan.")
        return phone

    def clean(self):
        """Parollar mosligini tekshiradi."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Parollar mos kelmadi.")
        return cleaned_data


# ------------------------------------------------------------------ #
#  LoginForm                                                           #
# ------------------------------------------------------------------ #

class LoginForm(forms.Form):
    """
    Kirish formasi.
    Requirement 2.1: phone_number va password maydonlari
    """

    phone_number = forms.CharField(
        max_length=20,
        label="Telefon raqami",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': '+998901234567',
            'autofocus': True,
        }),
        error_messages={'required': "Telefon raqami maydoni to'ldirilishi shart."},
    )

    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Parolingizni kiriting',
        }),
        error_messages={'required': "Parol maydoni to'ldirilishi shart."},
    )


# ------------------------------------------------------------------ #
#  BookForm                                                            #
# ------------------------------------------------------------------ #

class BookForm(forms.Form):
    """
    Kitob yaratish va tahrirlash formasi.
    Requirement 3.1: title, author, category, description, image, pdf_file, available
    """

    INPUT_CLASS = (
        'w-full px-4 py-2 border border-gray-300 rounded-lg '
        'focus:outline-none focus:ring-2 focus:ring-blue-500 '
        'dark:bg-gray-700 dark:border-gray-600 dark:text-white'
    )

    title = forms.CharField(
        max_length=255,
        label="Sarlavha",
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Kitob sarlavhasini kiriting',
        }),
        error_messages={'required': "Sarlavha maydoni to'ldirilishi shart."},
    )

    author = forms.CharField(
        max_length=255,
        label="Muallif",
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Muallif ismini kiriting',
        }),
        error_messages={'required': "Muallif maydoni to'ldirilishi shart."},
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # __init__ da yangilanadi
        label="Kategoriya",
        empty_label="Kategoriyani tanlang",
        widget=forms.Select(attrs={
            'class': INPUT_CLASS,
        }),
        error_messages={'required': "Kategoriya tanlanishi shart."},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Har safar form yaratilganda yangi queryset olinadi
        self.fields['category'].queryset = Category.objects.all().order_by('name')

    description = forms.CharField(
        label="Tavsif",
        required=False,
        widget=forms.Textarea(attrs={
            'class': INPUT_CLASS,
            'rows': 4,
            'placeholder': 'Kitob haqida qisqacha ma\'lumot',
        }),
    )

    image = forms.ImageField(
        label="Muqova rasmi",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': (
                'w-full text-sm text-gray-500 '
                'file:mr-4 file:py-2 file:px-4 '
                'file:rounded-lg file:border-0 '
                'file:text-sm file:font-semibold '
                'file:bg-blue-50 file:text-blue-700 '
                'hover:file:bg-blue-100'
            ),
            'accept': 'image/jpeg,image/png,image/webp',
        }),
        error_messages={'invalid_image': "Yuklangan fayl rasm emas yoki buzilgan."},
    )

    pdf_file = forms.FileField(
        label="PDF fayl",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': (
                'w-full text-sm text-gray-500 '
                'file:mr-4 file:py-2 file:px-4 '
                'file:rounded-lg file:border-0 '
                'file:text-sm file:font-semibold '
                'file:bg-green-50 file:text-green-700 '
                'hover:file:bg-green-100'
            ),
            'accept': 'application/pdf',
        }),
    )

    available = forms.BooleanField(
        label="Mavjud (ijaraga olish mumkin)",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500',
        }),
    )

    def clean_title(self):
        """title bo'sh bo'lmasligi kerak. Requirement 3.3"""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError("Sarlavha maydoni to'ldirilishi shart.")
        return title

    def clean_author(self):
        """author bo'sh bo'lmasligi kerak. Requirement 3.3"""
        author = self.cleaned_data.get('author', '').strip()
        if not author:
            raise ValidationError("Muallif maydoni to'ldirilishi shart.")
        return author


# ------------------------------------------------------------------ #
#  ProfileUpdateForm                                                   #
# ------------------------------------------------------------------ #

class ProfileUpdateForm(forms.Form):
    """
    Profil yangilash formasi.
    Requirements: 7.3, 7.4
    """

    INPUT_CLASS = (
        'w-full px-4 py-2 border border-gray-300 rounded-lg '
        'focus:outline-none focus:ring-2 focus:ring-blue-500 '
        'dark:bg-gray-700 dark:border-gray-600 dark:text-white'
    )

    first_name = forms.CharField(
        max_length=150,
        label="Ism",
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Ismingiz'}),
        error_messages={'required': "Ism maydoni to'ldirilishi shart."},
    )

    last_name = forms.CharField(
        max_length=150,
        label="Familiya",
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Familiyangiz'}),
        error_messages={'required': "Familiya maydoni to'ldirilishi shart."},
    )

    email = forms.EmailField(
        max_length=254,
        label="Email",
        widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'email@example.com'}),
        error_messages={
            'required': "Email maydoni to'ldirilishi shart.",
            'invalid': "Email formati noto'g'ri.",
        },
    )


# ------------------------------------------------------------------ #
#  CategoryForm                                                        #
# ------------------------------------------------------------------ #

from library.models import Category as CategoryModel

_CAT_INPUT_CLASS = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg '
    'focus:outline-none focus:ring-2 focus:ring-blue-500 '
    'dark:bg-gray-700 dark:border-gray-600 dark:text-white'
)


class CategoryForm(forms.ModelForm):
    """
    Kategoriya yaratish va tahrirlash formasi.
    Requirements: 9.1, 9.2, 9.4
    """

    class Meta:
        model = CategoryModel
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': _CAT_INPUT_CLASS,
                'placeholder': 'Kategoriya nomi',
            }),
        }
        error_messages = {
            'name': {
                'required': "Kategoriya nomi to'ldirilishi shart.",
                'unique': "Bu nom bilan kategoriya allaqachon mavjud.",
            }
        }
