"""
BorrowService — kitob ijarasi va qaytarish jarayonini boshqaradi.
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
"""

from django.http import Http404

from library.models import Book, Borrow, User


class BorrowServiceError(Exception):
    """BorrowService xatolari uchun exception."""
    pass


class BorrowService:
    """
    Kitob ijarasi va qaytarish jarayonini boshqaruvchi servis.
    """

    @staticmethod
    def is_book_available(book_id: int) -> bool:
        """
        Kitob mavjudligini tekshiradi.
        Requirement 6.4
        """
        try:
            book = Book.objects.get(pk=book_id)
            return book.available
        except Book.DoesNotExist:
            return False

    @staticmethod
    def borrow_book(user: User, book_id: int) -> Borrow:
        """
        Foydalanuvchi uchun kitob ijaraga olish yozuvini yaratadi.
        Requirements: 6.1, 6.2, 6.4

        :param user: ijaraga oluvchi foydalanuvchi
        :param book_id: kitob ID'si
        :returns: yaratilgan Borrow yozuvi
        :raises Http404: kitob topilmasa
        :raises BorrowServiceError: kitob mavjud bo'lmasa
        """
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise Http404("Kitob topilmadi.")

        if not book.available:
            raise BorrowServiceError(
                "Bu kitob hozirda mavjud emas. Boshqa foydalanuvchi ijarada."
            )

        # Borrow yozuvi yaratish — Requirement 6.1
        borrow = Borrow.objects.create(user=user, book=book)

        # Kitob mavjudligini yangilash — Requirement 6.2
        book.available = False
        book.save(update_fields=['available'])

        return borrow

    @staticmethod
    def return_book(borrow_id: int) -> Borrow:
        """
        Kitobni qaytaradi — borrow.returned=True, book.available=True.
        Requirement 6.6

        :param borrow_id: Borrow yozuvi ID'si
        :returns: yangilangan Borrow yozuvi
        :raises Http404: borrow yozuvi topilmasa
        :raises BorrowServiceError: kitob allaqachon qaytarilgan bo'lsa
        """
        try:
            borrow = Borrow.objects.select_related('book').get(pk=borrow_id)
        except Borrow.DoesNotExist:
            raise Http404("Ijara yozuvi topilmadi.")

        if borrow.returned:
            raise BorrowServiceError("Bu kitob allaqachon qaytarilgan.")

        borrow.returned = True
        borrow.save(update_fields=['returned'])

        borrow.book.available = True
        borrow.book.save(update_fields=['available'])

        return borrow

    @staticmethod
    def get_user_borrows(user: User):
        """
        Foydalanuvchining barcha ijara yozuvlarini qaytaradi.
        Requirement 7.2
        """
        return Borrow.objects.filter(user=user).select_related('book', 'book__category').order_by('-borrowed_at')

    @staticmethod
    def get_active_borrows(user: User):
        """
        Foydalanuvchining faol (qaytarilmagan) ijara yozuvlarini qaytaradi.
        Requirement 7.5
        """
        return Borrow.objects.filter(user=user, returned=False).select_related('book')
