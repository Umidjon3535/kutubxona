"""
Kitob view'lari — BookListView, BookDetailView va Admin kitob view'lari.
Requirements: 3.1–3.5, 4.1, 4.3, 4.5, 4.6, 4.7, 5.1
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View

from library.decorators import admin_required
from library.forms import BookForm
from library.models import Book, Category
from library.services.book_service import BookService


# ------------------------------------------------------------------ #
#  BookListView — barcha foydalanuvchilar uchun (login talab qilinmaydi)
# ------------------------------------------------------------------ #

class BookListView(View):
    """
    Kitoblar ro'yxati sahifasi.
    GET /books/ — qidiruv, kategoriya filtri va sahifalash bilan.
    Requirements: 4.1, 4.3, 4.5, 4.6, 13.1, 13.2, 13.3, 13.4, 13.5
    """

    template_name = 'books/list.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()
        category_id = request.GET.get('category', '').strip()
        page = request.GET.get('page', 1)

        filters = {
            'query': query,
            'category_id': category_id if category_id else None,
        }

        page_obj = BookService.list_books(filters=filters, page=page)

        # Out-of-bounds redirect — Requirement 13.3
        # list_books() allaqachon oxirgi sahifaga tushiradi, lekin URL'ni ham yangilash kerak
        try:
            requested_page = int(page)
        except (ValueError, TypeError):
            requested_page = 1

        if page_obj.paginator.num_pages > 0 and requested_page > page_obj.paginator.num_pages:
            # Oxirgi sahifaga redirect, qidiruv parametrlarini saqlab
            redirect_url = self._build_redirect_url(
                request, page_obj.paginator.num_pages, query, category_id
            )
            return redirect(redirect_url)

        categories = Category.objects.all().order_by('name')

        context = {
            'page_obj': page_obj,
            'books': page_obj.object_list,
            'query': query,
            'selected_category': category_id,
            'categories': categories,
            'total_count': page_obj.paginator.count,
        }
        return render(request, self.template_name, context)

    @staticmethod
    def _build_redirect_url(request, page_num, query, category_id):
        """Sahifalash redirect URL'ini quradi, qidiruv parametrlarini saqlab."""
        params = [f'page={page_num}']
        if query:
            params.append(f'q={query}')
        if category_id:
            params.append(f'category={category_id}')
        return f'/books/?{"&".join(params)}'


# ------------------------------------------------------------------ #
#  BookDetailView — barcha foydalanuvchilar uchun (login talab qilinmaydi)
# ------------------------------------------------------------------ #

class BookDetailView(View):
    """
    Kitob tafsilot sahifasi.
    GET /books/<id>/ — kitob haqida to'liq ma'lumot.
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """

    template_name = 'books/detail.html'

    def get(self, request, book_id):
        # Http404 ko'taradi agar kitob topilmasa — Requirement 5.1
        book = BookService.get_book(book_id)

        context = {
            'book': book,
        }
        return render(request, self.template_name, context)


# ------------------------------------------------------------------ #
#  AdminBookCreateView — faqat admin uchun
# ------------------------------------------------------------------ #

@method_decorator(admin_required, name='dispatch')
class AdminBookCreateView(View):
    """
    Admin: yangi kitob qo'shish.
    GET  /admin-panel/books/create/ — formani ko'rsatadi
    POST /admin-panel/books/create/ — kitobni saqlaydi
    Requirements: 3.1, 3.2, 3.3
    """

    template_name = 'admin_panel/book_form.html'

    def get(self, request):
        form = BookForm(initial={'available': True})
        return render(request, self.template_name, {
            'form': form,
            'action': 'create',
            'page_title': 'Yangi kitob qo\'shish',
        })

    def post(self, request):
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                book = BookService.create_book(
                    data={
                        'title': cd['title'],
                        'author': cd['author'],
                        'category': cd['category'],
                        'description': cd.get('description', ''),
                        'available': cd.get('available', True),
                    },
                    image=cd.get('image'),
                    pdf_file=cd.get('pdf_file'),
                )
                messages.success(
                    request,
                    f"'{book.title}' kitobi muvaffaqiyatli qo'shildi."
                )
                return redirect(f'/books/{book.pk}/')
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field if field in form.fields else None, error)
                else:
                    messages.error(request, str(e.message))

        return render(request, self.template_name, {
            'form': form,
            'action': 'create',
            'page_title': 'Yangi kitob qo\'shish',
        })


# ------------------------------------------------------------------ #
#  AdminBookUpdateView — faqat admin uchun
# ------------------------------------------------------------------ #

@method_decorator(admin_required, name='dispatch')
class AdminBookUpdateView(View):
    """
    Admin: mavjud kitobni tahrirlash.
    GET  /admin-panel/books/<id>/edit/ — formani ko'rsatadi
    POST /admin-panel/books/<id>/edit/ — o'zgarishlarni saqlaydi
    Requirements: 3.4
    """

    template_name = 'admin_panel/book_form.html'

    def get(self, request, book_id):
        book = BookService.get_book(book_id)
        form = BookForm(initial={
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'description': book.description,
            'available': book.available,
        })
        return render(request, self.template_name, {
            'form': form,
            'book': book,
            'action': 'update',
            'page_title': f"'{book.title}' kitobini tahrirlash",
        })

    def post(self, request, book_id):
        book = BookService.get_book(book_id)
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                updated_book = BookService.update_book(
                    book_id=book_id,
                    data={
                        'title': cd['title'],
                        'author': cd['author'],
                        'category': cd['category'],
                        'description': cd.get('description', ''),
                        'available': cd.get('available', True),
                    },
                    image=cd.get('image'),
                    pdf_file=cd.get('pdf_file'),
                )
                messages.success(
                    request,
                    f"'{updated_book.title}' kitobi muvaffaqiyatli yangilandi."
                )
                return redirect(f'/books/{updated_book.pk}/')
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field if field in form.fields else None, error)
                else:
                    messages.error(request, str(e.message))

        return render(request, self.template_name, {
            'form': form,
            'book': book,
            'action': 'update',
            'page_title': f"'{book.title}' kitobini tahrirlash",
        })


# ------------------------------------------------------------------ #
#  AdminBookDeleteView — faqat admin uchun
# ------------------------------------------------------------------ #

@method_decorator(admin_required, name='dispatch')
class AdminBookDeleteView(View):
    """
    Admin: kitobni o'chirish.
    GET  /admin-panel/books/<id>/delete/ — tasdiqlash sahifasini ko'rsatadi
    POST /admin-panel/books/<id>/delete/ — kitobni o'chiradi
    Requirements: 3.5, 12.5
    """

    template_name = 'admin_panel/book_confirm_delete.html'

    def get(self, request, book_id):
        book = BookService.get_book(book_id)
        return render(request, self.template_name, {
            'book': book,
            'page_title': f"'{book.title}' kitobini o'chirish",
        })

    def post(self, request, book_id):
        book = BookService.get_book(book_id)
        book_title = book.title
        BookService.delete_book(book_id)
        messages.success(
            request,
            f"'{book_title}' kitobi muvaffaqiyatli o'chirildi."
        )
        return redirect('/books/')
