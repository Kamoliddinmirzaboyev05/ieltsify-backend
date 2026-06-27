from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReadingPassage

import re
import logging

logger = logging.getLogger('modules')

@receiver(post_save, sender=ReadingPassage)
def calculate_word_count(sender, instance, created, **kwargs):
    if instance.html_content and (instance.word_count is None):
        try:
            # HTML faylni o‘qib, matndan tag’larni olib tashlash
            html_file = instance.html_content.path
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # HTML teglarini olib tashlash
            text_only = re.sub(r'<[^>]+>', ' ', content)
            # So‘zlarni hisoblash
            words = text_only.split()
            instance.word_count = len(words)
            instance.save(update_fields=['word_count'])
        except Exception as e:
            # Agar xato bo‘lsa, log qilamiz (silent fail emas)
            logger.warning(f"Word count hisoblashda xato: {e}")
