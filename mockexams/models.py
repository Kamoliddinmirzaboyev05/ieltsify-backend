"""
Full Mock Exam Models
=====================
IELTSify platformasi uchun to'liq mock imtihon moduli.
Core Mock: Listening + Reading + Writing
Complete Mock: Listening + Reading + Writing + Speaking
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class MockExam(models.Model):
    """Admin tomonidan yaratilgan mock imtihon shabloni."""

    EXAM_TYPE_CHOICES = (
        ('academic', 'IELTS Academic'),
        ('general_training', 'IELTS General Training'),
    )

    MOCK_TYPE_CHOICES = (
        ('core', 'Core Mock (Listening + Reading + Writing)'),
        ('complete', 'Complete Mock (+ Speaking)'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    DIFFICULTY_CHOICES = (
        ('easy', 'Easy (Band 5-6)'),
        ('medium', 'Medium (Band 6-7)'),
        ('hard', 'Hard (Band 7.5-9)'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='academic')
    mock_type = models.CharField(max_length=20, choices=MOCK_TYPE_CHOICES, default='core')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')

    # Linked content
    listening_test = models.ForeignKey(
        'modules.ListeningTest', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='mock_exams'
    )
    reading_test = models.ForeignKey(
        'modules.ReadingPassage', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='mock_exams'
    )
    writing_task1 = models.ForeignKey(
        'modules.WritingTask', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='mock_exams_task1'
    )
    writing_task2 = models.ForeignKey(
        'modules.WritingTask', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='mock_exams_task2'
    )
    # Speaking questions stored as JSON for flexibility
    speaking_questions = models.JSONField(
        blank=True, null=True,
        help_text="Speaking savollar to'plami: {part1: [...], part2: {...}, part3: [...]}"
    )

    estimated_duration_minutes = models.PositiveIntegerField(default=150)
    is_premium = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='created_mock_exams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mock Exam"
        verbose_name_plural = "Mock Exams"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_exam_type_display()} - {self.get_mock_type_display()})"


class MockExamQuota(models.Model):
    """Foydalanuvchining mock exam quotasi (tarif davri uchun)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='mock_quotas'
    )
    subscription = models.ForeignKey(
        'subscriptions.UserSubscription', on_delete=models.CASCADE,
        blank=True, null=True, related_name='mock_quotas'
    )

    core_mock_total = models.PositiveIntegerField(default=0)
    core_mock_used = models.PositiveIntegerField(default=0)
    complete_mock_total = models.PositiveIntegerField(default=0)
    complete_mock_used = models.PositiveIntegerField(default=0)

    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mock Exam Quota"
        verbose_name_plural = "Mock Exam Quotas"
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.user.email} - Core: {self.core_mock_used}/{self.core_mock_total}, Complete: {self.complete_mock_used}/{self.complete_mock_total}"

    @property
    def core_remaining(self):
        return max(0, self.core_mock_total - self.core_mock_used)

    @property
    def complete_remaining(self):
        return max(0, self.complete_mock_total - self.complete_mock_used)

    @property
    def is_active(self):
        now = timezone.now()
        return self.period_start <= now <= self.period_end


class MockExamAttempt(models.Model):
    """Foydalanuvchining mock imtihon urinishi."""

    STATUS_CHOICES = (
        ('reserved', 'Reserved'),
        ('in_progress', 'In Progress'),
        ('listening_completed', 'Listening Completed'),
        ('reading_completed', 'Reading Completed'),
        ('writing_completed', 'Writing Completed'),
        ('speaking_pending', 'Speaking Pending'),
        ('speaking_completed', 'Speaking Completed'),
        ('processing', 'Processing Results'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )

    ACCESS_SOURCE_CHOICES = (
        ('subscription_quota', 'Subscription Quota'),
        ('coin_purchase', 'Coin Purchase'),
        ('admin_grant', 'Admin Grant'),
        ('promo', 'Promo Code'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='mock_attempts'
    )
    mock_exam = models.ForeignKey(
        MockExam, on_delete=models.CASCADE,
        related_name='attempts'
    )

    exam_type = models.CharField(max_length=20, choices=MockExam.EXAM_TYPE_CHOICES)
    mock_type = models.CharField(max_length=20, choices=MockExam.MOCK_TYPE_CHOICES)
    access_source = models.CharField(max_length=20, choices=ACCESS_SOURCE_CHOICES, default='subscription_quota')
    coin_transaction_id = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='reserved')

    # Timing
    started_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Section timing
    listening_started_at = models.DateTimeField(blank=True, null=True)
    listening_completed_at = models.DateTimeField(blank=True, null=True)
    reading_started_at = models.DateTimeField(blank=True, null=True)
    reading_completed_at = models.DateTimeField(blank=True, null=True)
    writing_started_at = models.DateTimeField(blank=True, null=True)
    writing_completed_at = models.DateTimeField(blank=True, null=True)
    speaking_started_at = models.DateTimeField(blank=True, null=True)
    speaking_completed_at = models.DateTimeField(blank=True, null=True)

    # Current position
    current_section = models.CharField(max_length=20, default='listening')
    current_question = models.PositiveIntegerField(default=0)

    # Idempotency
    idempotency_key = models.CharField(max_length=100, unique=True, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mock Exam Attempt"
        verbose_name_plural = "Mock Exam Attempts"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'mock_exam']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.mock_exam.title} ({self.status})"


class MockExamAnswer(models.Model):
    """Foydalanuvchining javoblari (Reading/Listening)."""

    SECTION_CHOICES = (
        ('listening', 'Listening'),
        ('reading', 'Reading'),
    )

    attempt = models.ForeignKey(
        MockExamAttempt, on_delete=models.CASCADE,
        related_name='answers'
    )
    section_type = models.CharField(max_length=20, choices=SECTION_CHOICES)
    question_number = models.PositiveIntegerField()
    answer = models.TextField(blank=True)
    is_correct = models.BooleanField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mock Exam Answer"
        verbose_name_plural = "Mock Exam Answers"
        unique_together = ('attempt', 'section_type', 'question_number')
        ordering = ['section_type', 'question_number']

    def __str__(self):
        return f"Q{self.question_number} ({self.section_type}) - {self.attempt.user.email}"


class MockWritingSubmission(models.Model):
    """Writing javoblari."""

    TASK_TYPE_CHOICES = (
        ('task1', 'Task 1'),
        ('task2', 'Task 2'),
    )

    attempt = models.ForeignKey(
        MockExamAttempt, on_delete=models.CASCADE,
        related_name='writing_submissions'
    )
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES)
    content = models.TextField(blank=True)
    word_count = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(blank=True, null=True)

    # AI Feedback (JSON)
    ai_feedback = models.JSONField(blank=True, null=True)
    band_score = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "Mock Writing Submission"
        verbose_name_plural = "Mock Writing Submissions"
        unique_together = ('attempt', 'task_type')

    def __str__(self):
        return f"{self.task_type} - {self.attempt.user.email}"


class MockSpeakingRecording(models.Model):
    """Speaking audio yozuvlari."""

    PART_CHOICES = (
        ('part1', 'Part 1'),
        ('part2', 'Part 2'),
        ('part3', 'Part 3'),
    )

    attempt = models.ForeignKey(
        MockExamAttempt, on_delete=models.CASCADE,
        related_name='speaking_recordings'
    )
    speaking_part = models.CharField(max_length=10, choices=PART_CHOICES)
    question_number = models.PositiveIntegerField(default=1)
    audio_file = models.FileField(upload_to='mock_speaking/%Y/%m/', blank=True, null=True)
    transcript = models.TextField(blank=True)
    duration_seconds = models.FloatField(default=0)

    # AI Feedback
    ai_feedback = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mock Speaking Recording"
        verbose_name_plural = "Mock Speaking Recordings"
        ordering = ['speaking_part', 'question_number']

    def __str__(self):
        return f"{self.speaking_part} Q{self.question_number} - {self.attempt.user.email}"


class MockExamResult(models.Model):
    """Yakuniy natija va tahlil."""

    attempt = models.OneToOneField(
        MockExamAttempt, on_delete=models.CASCADE,
        related_name='result'
    )

    # Scores
    listening_correct = models.PositiveIntegerField(default=0)
    listening_total = models.PositiveIntegerField(default=40)
    listening_band = models.FloatField(blank=True, null=True)

    reading_correct = models.PositiveIntegerField(default=0)
    reading_total = models.PositiveIntegerField(default=40)
    reading_band = models.FloatField(blank=True, null=True)

    writing_band = models.FloatField(blank=True, null=True)
    speaking_band = models.FloatField(blank=True, null=True)
    overall_band = models.FloatField(blank=True, null=True)

    # Detailed breakdown (JSON)
    skill_breakdown = models.JSONField(blank=True, null=True)
    weak_skills = models.JSONField(blank=True, null=True)
    strong_skills = models.JSONField(blank=True, null=True)
    recommendations = models.JSONField(blank=True, null=True)
    question_type_accuracy = models.JSONField(blank=True, null=True)

    # Writing detailed
    writing_task1_feedback = models.JSONField(blank=True, null=True)
    writing_task2_feedback = models.JSONField(blank=True, null=True)

    # Speaking detailed
    speaking_feedback = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mock Exam Result"
        verbose_name_plural = "Mock Exam Results"

    def __str__(self):
        return f"Result: {self.attempt.user.email} - Overall {self.overall_band}"
