"""
Home va error view'lari.
Requirements: 10.3, 10.4, 10.5
"""

from django.shortcuts import render
from django.db.models import Count

from library.models import Book, Category


class HomeView:
    """
    Bosh sahifa view'i.
    GET /
    Requirements: 10.3, 10.4, 10.5
    """

    @staticmethod
    def get(request):
        # So'nggi 8 ta qo'shilgan kitob — Requirement 10.4
        recently_added = Book.objects.select_related('category').order_by('-created_at')[:8]

        # Eng mashhur kitoblar (ijara soni bo'yicha) — Requirement 10.5
        most_popular = Book.objects.select_related('category').annotate(
            borrow_count=Count('borrows')
        ).order_by('-borrow_count')[:8]

        # Kategoriyalar
        categories = Category.objects.all().order_by('name')

        # Statistika
        from library.models import Borrow, User
        total_books = Book.objects.count()
        total_users = User.objects.count()
        available_books = Book.objects.filter(available=True).count()

        context = {
            'recently_added': recently_added,
            'most_popular': most_popular,
            'categories': categories,
            'total_books': total_books,
            'total_users': total_users,
            'available_books': available_books,
        }
        return render(request, 'home.html', context)


def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    return render(request, 'errors/500.html', status=500)


def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)
