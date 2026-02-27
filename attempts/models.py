from django.conf import settings
from django.db import models


class UserDailyUsage(models.Model):
    """
    Foydalanuvchining kunlik foydalanish statistikasi:
    - vocab soni
    - writing evaluation soni
    - speaking mock soni
    - reading/listening attempts (kerak bo'lsa)
    Shu model keyinchalik streak va action plan uchun ishlatiladi.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_usages",
    )
    date = models.DateField()

    vocab_learned_count = models.PositiveIntegerField(default=0)
    writing_evaluation_count = models.PositiveIntegerField(default=0)
    speaking_mock_count = models.PositiveIntegerField(default=0)
    reading_attempt_count = models.PositiveIntegerField(default=0)
    listening_attempt_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Daily Usage"
        verbose_name_plural = "User Daily Usages"
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.date}"


