from django.conf import settings
from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.Model):
    """
    Tarif rejalari:
    - Free
    - IELTSify Weekly
    - IELTSify Monthly
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Ichki kod (masalan: free, weekly, monthly)",
    )
    name = models.CharField(
        max_length=150,
        help_text="Frontend uchun chiroyli nom",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Tarif haqida qisqacha ma'lumot",
    )

    price_uzs = models.PositiveIntegerField(
        help_text="Narx (so'mda)",
    )
    launch_price_uzs = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Launch maxsus narx (bo'lmasa oddiy narx ishlatiladi)",
    )
    duration_days = models.PositiveIntegerField(
        help_text="Obuna davomiyligi (kunlarda)",
    )

    included_coins = models.PositiveIntegerField(
        default=0,
        help_text="Obuna olganda beriladigan bonus coin",
    )

    # AI limitlari (tarif ichida bepul)
    writing_ai_limit = models.PositiveIntegerField(
        default=0,
        help_text="Tarif ichidagi Writing AI tahlil limiti (0 = yo'q)",
    )
    speaking_ai_limit = models.PositiveIntegerField(
        default=0,
        help_text="Tarif ichidagi Speaking AI tahlil limiti (0 = yo'q)",
    )

    # Kunlik limitlar (fair-use)
    daily_reading_limit = models.PositiveIntegerField(
        default=1,
        help_text="Kunlik Reading passage limiti",
    )
    daily_listening_limit = models.PositiveIntegerField(
        default=1,
        help_text="Kunlik Listening section limiti",
    )
    daily_writing_ai_limit = models.PositiveIntegerField(
        default=5,
        help_text="Kunlik Writing AI limiti (fair-use)",
    )
    daily_speaking_ai_limit = models.PositiveIntegerField(
        default=5,
        help_text="Kunlik Speaking AI limiti (fair-use)",
    )

    # Cheksizlik flaglari
    is_unlimited_reading = models.BooleanField(default=False)
    is_unlimited_listening = models.BooleanField(default=False)
    is_unlimited_vocab = models.BooleanField(default=True)
    has_weekly_plan = models.BooleanField(default=False)
    has_advanced_analytics = models.BooleanField(default=False)
    has_smart_article = models.BooleanField(default=False)

    daily_vocab_limit = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Kunlik vocab limiti (None = cheksiz)",
    )

    # Launch narx faol yoki yo'q
    is_launch_price_active = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    badge = models.CharField(max_length=50, blank=True, null=True, help_text="Masalan: Tavsiya etiladi")
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Planlar"
        ordering = ["sort_order", "price_uzs"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    @property
    def effective_price(self):
        """Hozirgi amal qilayotgan narx"""
        if self.is_launch_price_active and self.launch_price_uzs:
            return self.launch_price_uzs
        return self.price_uzs


class UserSubscription(models.Model):
    """
    Foydalanuvchining amaldagi yoki tarixdagi obunalari.
    Bir foydalanuvchining bir vaqtning o'zida faqat bitta faol obunasi bo'lishi kerak (biz services darajasida nazorat qilamiz).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_subscriptions",
    )

    start_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Obuna boshlanish vaqti",
    )
    end_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Obuna tugash vaqti",
    )

    is_active = models.BooleanField(default=False)

    # Kelajak uchun
    auto_renew = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"
        ordering = ["-start_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} -> {self.plan} ({'active' if self.is_active else 'inactive'})"

    @property
    def is_current(self) -> bool:
        if not self.is_active or not self.start_at or not self.end_at:
            return False
        now = timezone.now()
        return self.start_at <= now <= self.end_at


class CoinWallet(models.Model):
    """
    Har bir foydalanuvchi uchun bitta joriy balans.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coin_wallet",
    )
    balance = models.PositiveIntegerField(
        default=0,
        help_text="Joriy tangalar soni",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coin Wallet"
        verbose_name_plural = "Coin Walletlar"

    def __str__(self) -> str:
        return f"{self.user.email} -> {self.balance} coin"


class CoinTransaction(models.Model):
    """
    Har bir tanga harakatini log qilish uchun.
    """

    TYPE_CHOICES = (
        ("subscription_bonus", "Subscription bonus"),
        ("coin_shop_purchase", "Coin shop purchase"),
        ("welcome_bonus", "Welcome bonus"),
        ("writing_evaluation", "AI Writing Evaluation"),
        ("speaking_mock", "AI Speaking Mock"),
        ("smart_article_translation", "Smart Article Translation"),
        ("manual_adjustment", "Manual adjustment"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coin_transactions",
        blank=True,
        null=True,
    )
    wallet = models.ForeignKey(
        CoinWallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        blank=True,
        null=True,
    )

    # Musbat - balansga qo'shish, manfiy - balansdan yechish
    amount = models.IntegerField(
        help_text="Musbat (depozit) yoki manfiy (yechish) tanga miqdori",
    )

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        blank=True,
        null=True,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )

    # Bog'liq obyektlar uchun generic sohalar (ixtiyoriy)
    related_object_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Masalan, writing attempt ID yoki article ID",
    )
    related_object_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Masalan, writing_attempt, smart_article va hokazo",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Coin Transaction"
        verbose_name_plural = "Coin Transactionlar"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "type"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.amount} coin ({self.type})"


class CoinPack(models.Model):
    """
    Coin Shop uchun paketlar:
    - 50 Coin = 7,900 UZS
    - 150 Coin = 17,900 UZS
    - 500 Coin = 44,900 UZS
    """

    name = models.CharField(max_length=150)
    coins = models.PositiveIntegerField()
    price_uzs = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coin Pack"
        verbose_name_plural = "Coin Packlar"
        ordering = ["price_uzs"]

    def __str__(self) -> str:
        return f"{self.name} - {self.coins} coin"


class CoinServiceCost(models.Model):
    """
    AI xizmatlarining coin narxlari.
    Admin paneldan boshqariladi.
    """
    SERVICE_CHOICES = (
        ("writing_task1", "Writing Task 1 AI tahlili"),
        ("writing_task2", "Writing Task 2 AI tahlili"),
        ("speaking_part1", "Speaking Part 1 AI tahlili"),
        ("speaking_part2", "Speaking Part 2 AI tahlili"),
        ("speaking_part3", "Speaking Part 3 AI tahlili"),
        ("speaking_full_mock", "Full Speaking Mock tahlili"),
        ("full_mock_report", "Full IELTS Mock Report"),
        ("ai_tutor", "Kengaytirilgan AI Tutor javobi"),
        ("core_mock_exam", "Core Mock Exam"),
        ("complete_mock_exam", "Complete Mock Exam"),
    )

    service_code = models.CharField(
        max_length=50,
        unique=True,
        choices=SERVICE_CHOICES,
    )
    name = models.CharField(max_length=150)
    cost_coins = models.PositiveIntegerField(help_text="Xizmat narxi (coin)")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Coin Service Cost"
        verbose_name_plural = "Coin Service Costs"
        ordering = ["service_code"]

    def __str__(self):
        return f"{self.name} → {self.cost_coins} coin"


class Payment(models.Model):
    """
    Click/Payme va boshqa provayderlar bilan ishlash uchun umumiy to'lov modeli.
    Bu model orqali:
    - Subscription plan uchun to'lov
    - Coin pack uchun to'lov
    ni yuritish mumkin.
    """

    PROVIDER_CLICK = "click"
    PROVIDER_PAYME = "payme"

    PROVIDER_CHOICES = (
        (PROVIDER_CLICK, "Click"),
        (PROVIDER_PAYME, "Payme"),
    )

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELED, "Canceled"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payments",
        help_text="Agar bu to'lov obuna uchun bo'lsa",
    )
    coin_pack = models.ForeignKey(
        CoinPack,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payments",
        help_text="Agar bu to'lov coin pack uchun bo'lsa",
    )

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        blank=True,
        null=True,
    )
    provider_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Click/Payme tomonidan beriladigan ID (trans_id / transaction_id va hokazo)",
    )

    amount_uzs = models.PositiveIntegerField(
        help_text="To'lov summasi (so'mda)",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # Integratsiya uchun qo'shimcha maydonlar
    extra_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Provayderdan kelgan qo'shimcha ma'lumotlar (request/response)",
    )

    receipt_image = models.ImageField(
        upload_to="payments/receipts/%Y/%m/",
        blank=True,
        null=True,
        help_text="To'lov cheki (screenshot yoki PDF)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.amount_uzs} so'm ({self.status})"


