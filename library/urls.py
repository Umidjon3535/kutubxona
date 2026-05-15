"""
library app URL konfiguratsiyasi — barcha URL'lar.
"""

from django.urls import path
from django.views.generic import RedirectView

from library.views.auth_views import RegisterView, LoginView, LogoutView
from library.views.book_views import (
    BookListView, BookDetailView,
    AdminBookCreateView, AdminBookUpdateView, AdminBookDeleteView,
)
from library.views.borrow_views import BorrowBookView, ReturnBookView
from library.views.profile_views import ProfileView, ProfileUpdateView
from library.views.admin_views import (
    AdminDashboardView, AdminUserListView, AdminBookListView,
    AdminBorrowListView, AdminCategoryView,
)
from library.views.home_views import HomeView

app_name = 'library'

urlpatterns = [
    # ------------------------------------------------------------------ #
    #  Bosh sahifa                                                         #
    # ------------------------------------------------------------------ #
    path('', HomeView.get, name='home'),

    # ------------------------------------------------------------------ #
    #  Autentifikatsiya                                                    #
    # ------------------------------------------------------------------ #
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/',    LoginView.as_view(),    name='login'),
    path('auth/logout/',   LogoutView.as_view(),   name='logout'),

    # ------------------------------------------------------------------ #
    #  Kitoblar (ommaviy)                                                  #
    # ------------------------------------------------------------------ #
    path('books/',               BookListView.as_view(),    name='book_list'),
    path('books/<int:book_id>/', BookDetailView.as_view(),  name='book_detail'),

    # ------------------------------------------------------------------ #
    #  Ijara                                                               #
    # ------------------------------------------------------------------ #
    path('books/<int:book_id>/borrow/',   BorrowBookView.as_view(),  name='borrow_book'),
    path('borrows/<int:borrow_id>/return/', ReturnBookView.as_view(), name='return_book'),

    # ------------------------------------------------------------------ #
    #  Profil                                                              #
    # ------------------------------------------------------------------ #
    path('profile/',      ProfileView.as_view(),       name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),

    # ------------------------------------------------------------------ #
    #  Admin panel                                                         #
    # ------------------------------------------------------------------ #
    path('admin-panel/',             AdminDashboardView.as_view(),  name='admin_dashboard'),
    path('admin-panel/users/',       AdminUserListView.as_view(),   name='admin_users'),
    path('admin-panel/books/',       AdminBookListView.as_view(),   name='admin_books'),
    path('admin-panel/borrows/',     AdminBorrowListView.as_view(), name='admin_borrows'),
    path('admin-panel/categories/',  AdminCategoryView.as_view(),   name='admin_categories'),

    # Admin kitob CRUD
    path('admin-panel/books/create/',              AdminBookCreateView.as_view(), name='admin_book_create'),
    path('admin-panel/books/<int:book_id>/edit/',  AdminBookUpdateView.as_view(), name='admin_book_edit'),
    path('admin-panel/books/<int:book_id>/delete/', AdminBookDeleteView.as_view(), name='admin_book_delete'),
]
