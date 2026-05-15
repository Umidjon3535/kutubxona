"""
Borrow view'lari — kitob ijaraga olish va qaytarish.
Requirements: 6.1–6.6
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.views import View

from library.decorators import login_required_redirect
from library.services.borrow_service import BorrowService, BorrowServiceError
from django.utils.decorators import method_decorator


@method_decorator(login_required_redirect, name='dispatch')
class BorrowBookView(View):
    """
    Kitob ijaraga olish.
    POST /books/<book_id>/borrow/
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """

    def post(self, request, book_id):
        try:
            BorrowService.borrow_book(user=request.user, book_id=book_id)
            messages.success(
                request,
                "Kitob muvaffaqiyatli ijaraga olindi! Yaxshi o'qishlar."
            )
        except BorrowServiceError as e:
            messages.error(request, str(e))

        return redirect(f'/books/{book_id}/')

    def get(self, request, book_id):
        return redirect(f'/books/{book_id}/')


@method_decorator(login_required_redirect, name='dispatch')
class ReturnBookView(View):
    """
    Kitobni qaytarish.
    POST /borrows/<borrow_id>/return/
    Requirement 6.6
    """

    def post(self, request, borrow_id):
        try:
            borrow = BorrowService.return_book(borrow_id=borrow_id)
            messages.success(
                request,
                f"'{borrow.book.title}' kitobi muvaffaqiyatli qaytarildi."
            )
        except BorrowServiceError as e:
            messages.error(request, str(e))

        return redirect('/profile/')

    def get(self, request, borrow_id):
        return redirect('/profile/')
