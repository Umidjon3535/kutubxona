"""
SearchEngine — kitoblarni qidirish va filtrlash.
Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 13.1, 13.2, 13.3, 13.4, 13.5
"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from library.models import Book, Category

PAGE_SIZE = 12


class SearchEngine:
    """
    Kitoblarni qidirish va filtrlash servisi.
    """

    @staticmethod
    def search(query: str = '', category_id=None, page: int = 1):
        """
        Kitoblarni qidiruv va kategoriya filtri bilan qaytaradi.
        Requirements: 4.1, 4.3, 13.1, 13.2

        :param query: title/author bo'yicha case-insensitive qidiruv
        :param category_id: kategoriya ID filtri
        :param page: sahifa raqami
        :returns: Page obyekti
        """
        queryset = Book.objects.select_related('category').order_by('-created_at')

        # Case-insensitive partial match — Requirement 4.1, 13.1
        if query and query.strip():
            q = query.strip()
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(author__icontains=q)
            )

        # Kategoriya filtri — Requirement 4.3
        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass

        paginator = Paginator(queryset, PAGE_SIZE)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            # Out-of-bounds — oxirgi sahifaga qaytarish (Requirement 13.3)
            page_obj = paginator.page(paginator.num_pages)

        return page_obj

    @staticmethod
    def filter_by_category(category_id: int, page: int = 1):
        """
        Faqat kategoriya bo'yicha filtrlash.
        Requirement 4.3
        """
        return SearchEngine.search(category_id=category_id, page=page)
