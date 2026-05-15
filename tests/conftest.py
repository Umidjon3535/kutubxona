"""
Pytest configuration and Hypothesis profiles for Online Kutubxona Tizimi.

Design doc reference: Testing Strategy — Property-Based Testing section.
"""

import django
import os
import pytest

from hypothesis import settings, HealthCheck

# ---------------------------------------------------------------------------
# Hypothesis profiles
# ---------------------------------------------------------------------------

# CI profile: 100 examples, strict
settings.register_profile(
    "ci",
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)

# Development profile: 50 examples, faster feedback
settings.register_profile(
    "dev",
    max_examples=50,
    suppress_health_check=[HealthCheck.too_slow],
)

# Quick smoke profile: 10 examples
settings.register_profile(
    "smoke",
    max_examples=10,
    suppress_health_check=[HealthCheck.too_slow],
)

# Load the active profile (default: ci; override via HYPOTHESIS_PROFILE env var)
_active_profile = os.environ.get("HYPOTHESIS_PROFILE", "ci")
settings.load_profile(_active_profile)


# ---------------------------------------------------------------------------
# pytest-django fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user(db):
    """Create a standard test user."""
    from library.models import User
    return User.objects.create_user(
        phone_number='+998901234567',
        password='testpass123',
        first_name='Test',
        last_name='User',
        email='testuser@example.com',
    )


@pytest.fixture
def admin_user(db):
    """Create an admin (staff) test user."""
    from library.models import User
    return User.objects.create_user(
        phone_number='+998900000001',
        password='adminpass123',
        first_name='Admin',
        last_name='User',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    from library.models import Category
    return Category.objects.create(name='Test Category')


@pytest.fixture
def book(db, category):
    """Create a test book."""
    from library.models import Book
    return Book.objects.create(
        title='Test Book',
        author='Test Author',
        category=category,
        description='Test description',
        available=True,
    )
