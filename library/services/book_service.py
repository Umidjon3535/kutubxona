"""
BookService — kitob CRUD operatsiyalarini boshqaradi.
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.3, 4.6, 13.1, 13.2
"""

import os

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404

from library.models import Book, Category


# Bir sahifada ko'rsatiladigan kitoblar soni (Requirement 4.6, 13.2)
PAGE_SIZE = 12


class BookServiceError(Exception):
    """BookService xatolari uchun asosiy exception."""
    pass


class BookService:
    """
    Kitob CRUD operatsiyalarini boshqaruvchi servis.
    Design: BookService
    """

    # ------------------------------------------------------------------ #
    #  create_book                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def create_book(data: dict, image=None, pdf_file=None) -> Book:
        """
        Yangi kitob yaratadi va ma'lumotlar bazasiga saqlaydi.
        Requirement 3.2

        :param data: {title, author, category (Category instance yoki id),
                      description, available}
        :param image: yuklangan rasm fayli (yoki None)
        :param pdf_file: yuklangan PDF fayli (yoki None)
        :returns: yaratilgan Book obyekti
        :raises ValidationError: majburiy maydonlar bo'sh bo'lsa
        """
        BookService._validate_required_fields(data)

        category = BookService._resolve_category(data.get('category'))

        book = Book(
            title=data['title'].strip(),
            author=data['author'].strip(),
            category=category,
            description=data.get('description', '').strip(),
            available=data.get('available', True),
        )
        if image:
            book.image = image
        if pdf_file:
            book.pdf_file = pdf_file

        book.save()
        return book

    # ------------------------------------------------------------------ #
    #  update_book                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def update_book(book_id: int, data: dict, image=None, pdf_file=None) -> Book:
        """
        Mavjud kitobni yangilaydi.
        Requirement 3.4

        :param book_id: yangilanadigan kitob ID'si
        :param data: yangilash uchun maydonlar
        :param image: yangi rasm fayli (yoki None — o'zgartirmaslik)
        :param pdf_file: yangi PDF fayli (yoki None — o'zgartirmaslik)
        :returns: yangilangan Book obyekti
        :raises Http404: kitob topilmasa
        :raises ValidationError: majburiy maydonlar bo'sh bo'lsa
        """
        book = BookService.get_book(book_id)
        BookService._validate_required_fields(data)

        category = BookService._resolve_category(data.get('category'))

        book.title = data['title'].strip()
        book.author = data['author'].strip()
        book.category = category
        book.description = data.get('description', '').strip()
        book.available = data.get('available', book.available)

        if image:
            book.image = image
        if pdf_file:
            book.pdf_file = pdf_file

        book.save()
        return book

    # ------------------------------------------------------------------ #
    #  delete_book                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def delete_book(book_id: int) -> None:
        """
        Kitobni va unga bog'liq media fayllarni o'chiradi.
        Requirement 3.5, 12.5

        Media fayllar os.remove() orqali o'chiriladi.
        Keyinroq MediaStorage bilan integratsiya qilinadi.

        :param book_id: o'chiriladigan kitob ID'si
        :raises Http404: kitob topilmasa
        """
        book = BookService.get_book(book_id)

        # Media fayllarni o'chirish (Requirement 3.5, 12.5)
        BookService._delete_media_files(book)

        book.delete()

    # ------------------------------------------------------------------ #
    #  get_book                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_book(book_id: int) -> Book:
        """
        ID bo'yicha kitobni qaytaradi.
        Requirement 5.1

        :param book_id: kitob ID'si
        :returns: Book obyekti
        :raises Http404: kitob topilmasa
        """
        try:
            return Book.objects.select_related('category').get(pk=book_id)
        except Book.DoesNotExist:
            raise Http404(f"Kitob topilmadi (ID={book_id})")

    # ------------------------------------------------------------------ #
    #  list_books                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def list_books(filters: dict = None, page: int = 1):
        """
        Kitoblar ro'yxatini qaytaradi — qidiruv, kategoriya filtri va sahifalash bilan.
        Requirements: 4.1, 4.3, 4.6, 13.1, 13.2

        :param filters: {
            'query': str — title/author bo'yicha qidiruv (case-insensitive),
            'category_id': int | None — kategoriya filtri,
        }
        :param page: sahifa raqami
        :returns: django.core.paginator.Page obyekti
        """
        if filters is None:
            filters = {}

        queryset = Book.objects.select_related('category').order_by('-created_at')

        # Qidiruv filtri — Requirement 4.1, 13.1
        query = filters.get('query', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )

        # Kategoriya filtri — Requirement 4.3
        category_id = filters.get('category_id')
        if category_id:
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass

        # Sahifalash — Requirement 4.6, 13.2
        paginator = Paginator(queryset, PAGE_SIZE)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            # Out-of-bounds — oxirgi sahifaga qaytarish (Requirement 13.3)
            page_obj = paginator.page(paginator.num_pages)

        return page_obj

    # ------------------------------------------------------------------ #
    #  Yordamchi (private) metodlar                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_required_fields(data: dict) -> None:
        """
        title va author maydonlarini tekshiradi.
        Requirement 3.3
        """
        errors = {}
        if not data.get('title', '').strip():
            errors['title'] = "Kitob sarlavhasi to'ldirilishi shart."
        if not data.get('author', '').strip():
            errors['author'] = "Muallif ismi to'ldirilishi shart."
        if errors:
            raise ValidationError(errors)

    @staticmethod
    def _resolve_category(category) -> Category:
        """
        Category obyekti yoki ID'dan Category qaytaradi.
        """
        if isinstance(category, Category):
            return category
        if category is not None:
            try:
                return Category.objects.get(pk=int(category))
            except (Category.DoesNotExist, ValueError, TypeError):
                raise ValidationError({'category': "Tanlangan kategoriya mavjud emas."})
        raise ValidationError({'category': "Kategoriya tanlanishi shart."})

    @staticmethod
    def _delete_media_files(book: Book) -> None:
        """
        Kitobga bog'liq rasm va PDF fayllarni diskdan o'chiradi.
        Requirement 3.5, 12.5
        """
        for field in (book.image, book.pdf_file):
            if field and field.name:
                try:
                    file_path = field.path
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except (ValueError, OSError):
                    # Fayl mavjud bo'lmasa yoki o'chirishda xato bo'lsa — davom etamiz
                    pass
