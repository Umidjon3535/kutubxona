"""
Smoke tests for Task 2.1 — User, Category, Book, Borrow models.
Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
"""

import pytest
from django.db import IntegrityError
from library.models import User, Category, Book, Borrow


class TestUserModel:
    """Requirement 11.2: User model with phone_number field."""

    def test_user_has_phone_number_field(self):
        fields = [f.name for f in User._meta.get_fields()]
        assert 'phone_number' in fields

    def test_username_field_is_phone_number(self):
        assert User.USERNAME_FIELD == 'phone_number'

    def test_required_fields(self):
        assert set(User.REQUIRED_FIELDS) == {'first_name', 'last_name', 'email'}

    def test_user_db_table(self):
        assert User._meta.db_table == 'users'

    def test_create_user(self, db):
        user = User.objects.create_user(
            phone_number='+998901111111',
            password='securepass123',
            first_name='Ali',
            last_name='Valiyev',
            email='ali@example.com',
        )
        assert user.pk is not None
        assert user.phone_number == '+998901111111'
        assert user.first_name == 'Ali'

    def test_phone_number_unique(self, db):
        User.objects.create_user(
            phone_number='+998902222222',
            password='pass12345',
            first_name='A',
            last_name='B',
            email='a@example.com',
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                phone_number='+998902222222',
                password='pass12345',
                first_name='C',
                last_name='D',
                email='c@example.com',
            )

    def test_user_str(self, db):
        user = User.objects.create_user(
            phone_number='+998903333333',
            password='pass12345',
            first_name='Zafar',
            last_name='Toshmatov',
            email='zafar@example.com',
        )
        assert 'Zafar' in str(user)
        assert 'Toshmatov' in str(user)


class TestCategoryModel:
    """Requirement 11.4: Category model with name and slug."""

    def test_category_fields(self):
        fields = [f.name for f in Category._meta.get_fields()]
        assert 'name' in fields
        assert 'slug' in fields

    def test_category_db_table(self):
        assert Category._meta.db_table == 'categories'

    def test_slug_auto_generated(self, db):
        cat = Category.objects.create(name='Ilmiy Adabiyot')
        assert cat.slug == 'ilmiy-adabiyot'

    def test_slug_not_overwritten_if_set(self, db):
        cat = Category.objects.create(name='Test', slug='custom-slug')
        assert cat.slug == 'custom-slug'

    def test_category_name_unique(self, db):
        Category.objects.create(name='Unique Cat')
        with pytest.raises(IntegrityError):
            Category.objects.create(name='Unique Cat')

    def test_category_str(self, db):
        cat = Category.objects.create(name='Roman')
        assert str(cat) == 'Roman'


class TestBookModel:
    """Requirement 11.1: Book model with all required fields."""

    def test_book_fields(self):
        fields = [f.name for f in Book._meta.get_fields()]
        for field in ['title', 'author', 'category', 'description', 'image', 'pdf_file', 'available', 'created_at']:
            assert field in fields, f"'{field}' maydoni Book modelida yo'q"

    def test_book_db_table(self):
        assert Book._meta.db_table == 'books'

    def test_book_ordering(self):
        assert Book._meta.ordering == ['-created_at']

    def test_book_available_default_true(self, db, category):
        book = Book.objects.create(
            title='Test Kitob',
            author='Test Muallif',
            category=category,
        )
        assert book.available is True

    def test_book_category_on_delete_protect(self):
        from django.db.models import PROTECT
        field = Book._meta.get_field('category')
        assert field.remote_field.on_delete is PROTECT

    def test_book_str(self, db, category):
        book = Book.objects.create(
            title='Navoiy',
            author='Alisher Navoiy',
            category=category,
        )
        assert 'Navoiy' in str(book)
        assert 'Alisher Navoiy' in str(book)

    def test_book_created_at_auto(self, db, category):
        book = Book.objects.create(
            title='Auto Date Test',
            author='Author',
            category=category,
        )
        assert book.created_at is not None


class TestBorrowModel:
    """Requirement 11.3: Borrow model with cascade delete."""

    def test_borrow_fields(self):
        fields = [f.name for f in Borrow._meta.get_fields()]
        for field in ['user', 'book', 'borrowed_at', 'returned']:
            assert field in fields, f"'{field}' maydoni Borrow modelida yo'q"

    def test_borrow_db_table(self):
        assert Borrow._meta.db_table == 'borrows'

    def test_borrow_returned_default_false(self, db, user, book):
        borrow = Borrow.objects.create(user=user, book=book)
        assert borrow.returned is False

    def test_borrow_user_cascade_delete(self, db, user, book):
        """Requirement 11.6: Deleting user cascades to Borrow records."""
        borrow = Borrow.objects.create(user=user, book=book)
        borrow_id = borrow.pk
        user.delete()
        assert not Borrow.objects.filter(pk=borrow_id).exists()

    def test_borrow_book_cascade_delete(self, db, user, book):
        """Requirement 11.5: Deleting book cascades to Borrow records."""
        borrow = Borrow.objects.create(user=user, book=book)
        borrow_id = borrow.pk
        book.delete()
        assert not Borrow.objects.filter(pk=borrow_id).exists()

    def test_borrow_user_on_delete_cascade(self):
        from django.db.models import CASCADE
        field = Borrow._meta.get_field('user')
        assert field.remote_field.on_delete is CASCADE

    def test_borrow_book_on_delete_cascade(self):
        from django.db.models import CASCADE
        field = Borrow._meta.get_field('book')
        assert field.remote_field.on_delete is CASCADE

    def test_borrow_str(self, db, user, book):
        borrow = Borrow.objects.create(user=user, book=book)
        assert book.title in str(borrow)

    def test_borrow_ordering(self):
        assert Borrow._meta.ordering == ['-borrowed_at']
