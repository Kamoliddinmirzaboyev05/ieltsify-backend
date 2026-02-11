from django.db import models
from django.core.validators import MinLengthValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.text import slugify


class ListeningTest(models.Model):
    title = models.CharField(
        _("Sarlavha"),
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Masalan: IELTS Listening Practice Test 1"
    )

    slug = models.SlugField(
        _("Slug"),
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL uchun avtomatik generatsiya qilinadi (agar bo'sh qoldirilsa)"
    )

    description = models.TextField(
        _("Qisqacha tavsif"),
        blank=True,
        help_text="Test haqida qisqacha ma'lumot (ixtiyoriy)"
    )

    html_file = models.FileField(
        _("HTML fayl"),
        upload_to="listening_tests/html/%Y/%m/",
        help_text="Listening testning asosiy HTML fayli (audio + savollar bilan)"
    )

    cover_image = models.ImageField(
        _("Muqova rasmi"),
        upload_to="listening_tests/covers/%Y/%m/",
        blank=True,
        null=True,
        help_text="Test uchun muqova rasmi (ixtiyoriy)"
    )

    difficulty = models.CharField(
        _("Qiyinlik darajasi"),
        max_length=20,
        choices=[
            ('easy', 'Easy (Band 5-6)'),
            ('medium', 'Medium (Band 6-7)'),
            ('hard', 'Hard (Band 7.5-9)'),
        ],
        default='medium',
    )

    is_active = models.BooleanField(
        _("Faolmi"),
        default=True,
        help_text="Faqat faol testlar talabalar tomonidan ko'rinadi"
    )

    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)
    updated_at = models.DateTimeField(_("O'zgartirilgan sana"), auto_now=True)

    class Meta:
        verbose_name = _("Listening Test")
        verbose_name_plural = _("Listening Testlari")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "difficulty"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while ListeningTest.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ReadingPassage(models.Model):
    title = models.CharField(
        _("Sarlavha"),
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Masalan: The Nature of Memory, Urbanization Trends"
    )

    slug = models.SlugField(
        _("Slug"),
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL uchun (agar bo'sh qoldirilsa avto-generatsiya qilinadi)"
    )

    html_content = models.FileField(
        _("HTML fayl"),
        upload_to="reading_passages/html/%Y/%m/",
        help_text="Matn, sarlavhalar, rasmlar va formatlash HTML ichida bo'ladi"
    )

    cover_image = models.ImageField(
        _("Muqova rasmi"),
        upload_to="reading_passages/covers/%Y/%m/",
        blank=True,
        null=True,
        help_text="Passage uchun muqova/illustratsiya (ixtiyoriy)"
    )

    difficulty = models.CharField(
        _("Qiyinlik darajasi"),
        max_length=20,
        choices=[
            ('easy', 'Easy (Band 5-6)'),
            ('medium', 'Medium (Band 6-7)'),
            ('hard', 'Hard (Band 7.5-9)'),
        ],
        default='medium',
    )

    word_count = models.PositiveIntegerField(
        _("So'zlar soni"),
        blank=True,
        null=True,
        help_text="Matndagi taxminiy so'zlar soni (avto hisoblash mumkin)"
    )

    is_active = models.BooleanField(
        _("Faolmi"),
        default=True,
        help_text="Faqat faol passage talabalar uchun ko'rinadi"
    )

    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)
    updated_at = models.DateTimeField(_("O'zgartirilgan sana"), auto_now=True)

    class Meta:
        verbose_name = _("Reading Passage")
        verbose_name_plural = _("Reading Passages")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "difficulty"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while ReadingPassage.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Agar word_count hali kiritilmagan bo'lsa — keyinchalik signal orqali hisoblash mumkin
        super().save(*args, **kwargs)


class WritingTask(models.Model):
    title = models.CharField(
        _("Sarlavha / Mavzu"),
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Masalan: Environment & Technology, Housing Trends in the UK"
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL uchun (bo'sh qoldirsangiz avto generatsiya qilinadi)"
    )

    # Umumiy ma'lumotlar
    topic_category = models.CharField(
        _("Mavzu kategoriyasi"),
        max_length=100,
        blank=True,
        help_text="Masalan: Environment, Education, Technology, Health, Crime"
    )

    difficulty = models.CharField(
        _("Taxminiy band darajasi"),
        max_length=20,
        choices=[
            ('band_5_6', 'Band 5–6'),
            ('band_6_7', 'Band 6–7'),
            ('band_7_5_plus', 'Band 7.5+'),
        ],
        default='band_6_7',
        blank=True,
    )

    # Task 1 maydonlari
    task1_question = models.TextField(
        _("Task 1 savoli (Graph/Chart/Process/Map)"),
        blank=True,
        validators=[MinLengthValidator(20)],
        help_text="Masalan: The chart below shows the percentage of households..."
    )

    task1_image = models.ImageField(
        _("Task 1 diagrammasi / rasmi"),
        upload_to="writing/task1/%Y/%m/",
        blank=True,
        null=True,
        help_text="Graph, table, pie chart, bar chart, process diagram yoki map"
    )

    task1_word_count = models.PositiveSmallIntegerField(
        _("Task 1 minimal so'zlar"),
        default=150,
        help_text="Odatda 150+"
    )

    task1_time_minutes = models.PositiveSmallIntegerField(
        _("Task 1 vaqti (daqiqa)"),
        default=20,
    )

    # Task 2 maydonlari
    task2_question = models.TextField(
        _("Task 2 savoli (Essay)"),
        blank=True,
        validators=[MinLengthValidator(30)],
        help_text="Masalan: Some people think that technology makes life more complicated..."
    )

    task2_essay_type = models.CharField(
        _("Task 2 essay turi"),
        max_length=50,
        choices=[
            ('', '— tanlanmagan —'),
            ('opinion', 'Agree / Disagree'),
            ('discussion', 'Discuss both views'),
            ('advantages_disadvantages', 'Advantages & Disadvantages'),
            ('problem_solution', 'Problem & Solution'),
            ('two_part', 'Two-part question'),
        ],
        default='',
        blank=True,
    )

    task2_word_count = models.PositiveSmallIntegerField(
        _("Task 2 minimal so'zlar"),
        default=250,
        help_text="Odatda 250+"
    )

    task2_time_minutes = models.PositiveSmallIntegerField(
        _("Task 2 vaqti (daqiqa)"),
        default=40,
    )

    is_active = models.BooleanField(_("Faol"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writing Task (Task 1 + Task 2)"
        verbose_name_plural = "Writing Tasklari"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while WritingTask.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def has_task1(self):
        return bool(self.task1_question.strip())

    def has_task2(self):
        return bool(self.task2_question.strip())


class SmartArticle(models.Model):
    title = models.CharField(
        _("Sarlavha"),
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Masalan: Climate Change, The Benefits of Remote Work"
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL uchun (bo'sh qoldirsangiz avtomatik yaratiladi)"
    )

    content = models.TextField(
        _("Maqola matni"),
        validators=[MinLengthValidator(200)],
        help_text="To'liq maqola matni (Markdown yoki oddiy text bo'lishi mumkin)"
    )

    level = models.CharField(
        _("Daraja (Level)"),
        max_length=30,
        choices=[
            ('beginner', 'Beginner (A1–A2)'),
            ('elementary', 'Elementary (A2–B1)'),
            ('intermediate', 'Intermediate (B1–B2)'),
            ('upper_intermediate', 'Upper-Intermediate (B2–C1)'),
            ('advanced', 'Advanced (C1–C2)'),
        ],
        default='intermediate',
        help_text="Maqola qaysi darajadagi o'quvchilar uchun mo'ljallangan"
    )

    featured_image = models.ImageField(
        _("Rasm (muqova)"),
        upload_to="articles/featured/%Y/%m/",
        blank=True,
        null=True,
        help_text="Maqola uchun asosiy rasm (ixtiyoriy, lekin tavsiya etiladi)"
    )

    created_at = models.DateTimeField(_("Yaratilgan"), auto_now_add=True)
    updated_at = models.DateTimeField(_("O'zgartirilgan"), auto_now=True)

    class Meta:
        verbose_name = _("Smart Article")
        verbose_name_plural = _("Smart Articles")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["level", ]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while SmartArticle.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def word_count(self):
        return len(self.content.split()) if self.content else 0


class ListeningMaterial(models.Model):
    name = models.CharField(
        _("Nomi"),
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Masalan: IELTS Listening Practice Test 2025 | Section 1-4"
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL uchun avtomatik generatsiya qilinadi"
    )

    youtube_url = models.URLField(
        _("YouTube URL"),
        validators=[URLValidator()],
        help_text="To'liq YouTube video havolasi[](https://www.youtube.com/watch?v=...)"
    )

    category = models.CharField(
        _("Kategoriya"),
        max_length=100,
        choices=[
            ('section_1', 'Section 1 – Everyday Social Conversations'),
            ('section_2', 'Section 2 – Monologues (speeches, guides)'),
            ('section_3', 'Section 3 – Academic Discussions'),
            ('section_4', 'Section 4 – Lectures / Academic Monologues'),
            ('full_test', 'Full Listening Practice Test'),
            ('question_type', 'Specific Question Type Practice (Matching, MCQ, etc.)'),
            ('topic_based', 'Topic-based (Travel, Education, Environment, Work)'),
            ('tips_tricks', 'Tips & Strategies for IELTS Listening'),
            ('real_test_simulation', 'Real IELTS Test Simulation'),
        ],
        default='full_test',
        help_text="Material qaysi turdagi mashq ekanligini belgilaydi"
    )

    description = models.TextField(
        _("Qisqacha tavsif"),
        blank=True,
        max_length=500,
        help_text="Videoda nimalar borligi haqida qisqa ma'lumot (ixtiyoriy)"
    )

    difficulty = models.CharField(
        _("Qiyinlik darajasi"),
        max_length=20,
        choices=[
            ('beginner', 'Beginner / Band 4-5.5'),
            ('intermediate', 'Intermediate / Band 6-7'),
            ('advanced', 'Advanced / Band 7.5+'),
        ],
        default='intermediate',
        blank=True,
    )

    duration_minutes = models.PositiveSmallIntegerField(
        _("Taxminiy davomiylik (daqiqa)"),
        blank=True,
        null=True,
        help_text="Videoning taxminiy uzunligi (qo'lda yoki avto hisoblash mumkin)"
    )

    is_active = models.BooleanField(
        _("Faolmi"),
        default=True,
        help_text="Faqat faol materiallar talabalar uchun ko'rinadi"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Listening Material (YouTube)")
        verbose_name_plural = _("Listening Materiallari (YouTube)")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category", "difficulty", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while ListeningMaterial.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def youtube_id(self):
        """YouTube video ID sini qaytaradi (embed uchun foydali)"""
        if self.youtube_url:
            # Oddiy holatda ?v= dan keyingi qism
            if 'v=' in self.youtube_url:
                return self.youtube_url.split('v=')[1].split('&')[0]
            # qisqa url holati youtu.be/...
            elif 'youtu.be/' in self.youtube_url:
                return self.youtube_url.split('youtu.be/')[1].split('?')[0]
        return None


class Topic(models.Model):
    name = models.CharField(_("Mavzu nomi"), max_length=150, unique=True)

    class Meta:
        verbose_name = _("Mavzu")
        verbose_name_plural = _("Mavzular")

    def __str__(self):
        return self.name


class VocabularyWord(models.Model):
    word = models.CharField(
        _("So'z"),
        max_length=150,
        validators=[MinLengthValidator(2)]
    )
    definition = models.TextField(
        _("Ta'rif / Definition"),
        validators=[MinLengthValidator(10)]
    )
    cefr_level = models.CharField(
        _("CEFR darajasi"),
        max_length=5,
        choices=[
            ('A1', 'A1 – Beginner'),
            ('A2', 'A2 – Elementary'),
            ('B1', 'B1 – Intermediate'),
            ('B2', 'B2 – Upper-Intermediate'),
            ('C1', 'C1 – Advanced'),
            ('C2', 'C2 – Proficiency'),
        ],
        default='B1'
    )
    example_sentences = models.TextField(
        _("Misol jumlalar"),
        blank=True,
        help_text="Har bir jumla yangi qatordan yoziladi"
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="vocabulary_words", blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_vocabulary_words",
    )
    is_public = models.BooleanField(default=False)
    imported_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="imports"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Vocabulary Word")
        verbose_name_plural = _("Vocabulary Words")
        ordering = ["word"]
        indexes = [
            models.Index(fields=["word"]),
            models.Index(fields=["cefr_level"]),
        ]

    def __str__(self):
        return f"{self.word} ({self.cefr_level})"

    def get_example_sentences_list(self):
        if self.example_sentences:
            return [s.strip() for s in self.example_sentences.splitlines() if s.strip()]
        return []

    def save(self, *args, **kwargs):
        # Role asosida is_public belgilash
        if self.created_by:
            if hasattr(self.created_by, "role") and self.created_by.role == "admin":
                self.is_public = True
            else:
                self.is_public = False
        super().save(*args, **kwargs)
