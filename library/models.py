from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify


class CustomUserManager(BaseUserManager):
    """
    Custom manager for User model where phone_number is the unique identifier
    instead of username.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Telefon raqami kiritilishi shart')
        extra_fields.setdefault('is_active', True)
        # username ni phone_number bilan bir xil qilamiz (AbstractUser talab qiladi)
        extra_fields.setdefault('username', phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', phone_number)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo\'lishi kerak')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'lishi kerak')

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Uses phone_number as the USERNAME_FIELD for authentication.
    Requirement 11.2
    """
    phone_number = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class Category(models.Model):
    """
    Book category model.
    Requirement 11.4
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model with all required fields.
    Requirement 11.1
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='books'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='book_pdfs/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'books'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.author}"


class Borrow(models.Model):
    """
    Borrow record model.
    Requirement 11.3
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrows'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrows'
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned = models.BooleanField(default=False)

    class Meta:
        db_table = 'borrows'
        ordering = ['-borrowed_at']

    def __str__(self):
        return f"{self.user} — {self.book.title} ({'qaytarilgan' if self.returned else 'ijarada'})"
