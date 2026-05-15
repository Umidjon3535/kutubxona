"""
MediaStorage — rasm va PDF fayllarni validatsiya qiladi va o'chiradi.
Requirements: 3.6, 3.7, 3.8, 12.1, 12.2, 12.3, 12.5
"""

import os
from django.core.exceptions import ValidationError


class MediaStorage:
    """
    Rasm va PDF fayllarni saqlash va validatsiya qiluvchi servis.
    """

    MAX_IMAGE_SIZE = 5 * 1024 * 1024    # 5 MB
    MAX_PDF_SIZE   = 50 * 1024 * 1024   # 50 MB
    ALLOWED_IMAGE_FORMATS = ['image/jpeg', 'image/png', 'image/webp']

    @staticmethod
    def validate_image(file) -> None:
        """
        Rasm faylini format va hajm bo'yicha tekshiradi.
        Requirement 3.6, 3.8
        """
        if file is None:
            return
        if hasattr(file, 'content_type'):
            if file.content_type not in MediaStorage.ALLOWED_IMAGE_FORMATS:
                raise ValidationError(
                    "Faqat JPEG, PNG va WebP formatdagi rasmlar qabul qilinadi."
                )
        if file.size > MediaStorage.MAX_IMAGE_SIZE:
            raise ValidationError(
                f"Rasm fayli hajmi 5 MB dan oshmasligi kerak. "
                f"Yuklangan fayl: {file.size // (1024*1024)} MB"
            )

    @staticmethod
    def validate_pdf(file) -> None:
        """
        PDF faylini hajm bo'yicha tekshiradi.
        Requirement 3.7, 3.8
        """
        if file is None:
            return
        if file.size > MediaStorage.MAX_PDF_SIZE:
            raise ValidationError(
                f"PDF fayl hajmi 50 MB dan oshmasligi kerak. "
                f"Yuklangan fayl: {file.size // (1024*1024)} MB"
            )

    @staticmethod
    def delete_book_media(book) -> None:
        """
        Kitobga bog'liq rasm va PDF fayllarni diskdan o'chiradi.
        Requirement 3.5, 12.5
        """
        for field in (book.image, book.pdf_file):
            if field and field.name:
                try:
                    file_path = field.path
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except (ValueError, OSError):
                    pass
