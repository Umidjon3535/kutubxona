"""
Admin panel view'lari.
Requirements: 8.1–8.6, 9.1–9.4
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views import View

from library.decorators import admin_required
from library.models import User, Book, Borrow, Category
from library.forms import CategoryForm


@method_decorator(admin_required, name='dispatch')
class AdminDashboardView(View):
    """
    Admin dashboard — statistika ko'rsatadi.
    GET /admin-panel/
    Requirement 8.6
    """

    template_name = 'admin_panel/dashboard.html'

    def get(self, request):
        context = {
            'total_books': Book.objects.count(),
            'total_users': User.objects.count(),
            'active_borrows': Borrow.objects.filter(returned=False).count(),
            'available_books': Book.objects.filter(available=True).count(),
            'recent_borrows': Borrow.objects.select_related('user', 'book').order_by('-borrowed_at')[:10],
            'recent_books': Book.objects.select_related('category').order_by('-created_at')[:5],
        }
        return render(request, self.template_name, context)


@method_decorator(admin_required, name='dispatch')
class AdminUserListView(View):
    """
    Admin: foydalanuvchilar ro'yxati.
    GET /admin-panel/users/
    Requirements: 8.2, 8.4
    """

    template_name = 'admin_panel/users.html'

    def get(self, request):
        users = User.objects.order_by('-date_joined')
        paginator = Paginator(users, 20)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'users': page_obj.object_list,
        })

    def post(self, request):
        """Foydalanuvchini aktivlashtirish/deaktivlashtirish — Requirement 8.4"""
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        user = get_object_or_404(User, pk=user_id)

        if action == 'deactivate':
            user.is_active = False
            user.save(update_fields=['is_active'])
            messages.success(request, f"{user.get_full_name()} hisobi deaktivlashtirildi.")
        elif action == 'activate':
            user.is_active = True
            user.save(update_fields=['is_active'])
            messages.success(request, f"{user.get_full_name()} hisobi aktivlashtirildi.")

        return redirect('/admin-panel/users/')


@method_decorator(admin_required, name='dispatch')
class AdminBookListView(View):
    """
    Admin: kitoblar ro'yxati.
    GET /admin-panel/books/
    Requirement 8.1
    """

    template_name = 'admin_panel/books.html'

    def get(self, request):
        books = Book.objects.select_related('category').order_by('-created_at')
        paginator = Paginator(books, 20)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'books': page_obj.object_list,
        })


@method_decorator(admin_required, name='dispatch')
class AdminBorrowListView(View):
    """
    Admin: ijara tarixi ro'yxati.
    GET /admin-panel/borrows/
    Requirement 8.3
    """

    template_name = 'admin_panel/borrows.html'

    def get(self, request):
        borrows = Borrow.objects.select_related('user', 'book').order_by('-borrowed_at')
        paginator = Paginator(borrows, 20)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'borrows': page_obj.object_list,
        })


@method_decorator(admin_required, name='dispatch')
class AdminCategoryView(View):
    """
    Admin: kategoriyalar boshqaruvi (CRUD).
    GET  /admin-panel/categories/
    POST /admin-panel/categories/
    Requirements: 9.1, 9.2, 9.3, 9.4
    """

    template_name = 'admin_panel/categories.html'

    def get(self, request):
        categories = Category.objects.annotate(book_count=Count('books')).order_by('name')
        form = CategoryForm()
        return render(request, self.template_name, {
            'categories': categories,
            'form': form,
        })

    def post(self, request):
        action = request.POST.get('action', 'create')

        if action == 'create':
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save()
                messages.success(request, f"'{category.name}' kategoriyasi qo'shildi.")
                return redirect('/admin-panel/categories/')
            categories = Category.objects.annotate(book_count=Count('books')).order_by('name')
            return render(request, self.template_name, {
                'categories': categories,
                'form': form,
            })

        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            category = get_object_or_404(Category, pk=cat_id)
            book_count = category.books.count()

            if book_count > 0:
                # Tasdiqlash talab qilinadi — Requirement 9.3
                confirm = request.POST.get('confirm_delete')
                if confirm != 'yes':
                    messages.warning(
                        request,
                        f"'{category.name}' kategoriyasida {book_count} ta kitob bor. "
                        f"O'chirish uchun tasdiqlang."
                    )
                    return redirect(f'/admin-panel/categories/?confirm_delete={cat_id}')

            category.delete()
            messages.success(request, f"'{category.name}' kategoriyasi o'chirildi.")
            return redirect('/admin-panel/categories/')

        elif action == 'edit':
            cat_id = request.POST.get('category_id')
            category = get_object_or_404(Category, pk=cat_id)
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, f"Kategoriya muvaffaqiyatli yangilandi.")
                return redirect('/admin-panel/categories/')

        return redirect('/admin-panel/categories/')
