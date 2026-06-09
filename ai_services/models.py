"""
AI Services Models — Usage logs, Writing submissions, Speaking attempts.
"""
from django.conf import settings
from django.db import models


class AIUsageLog(models.Model):
    """Har bir AI chaqiruv logi."""

    SERVICE_TYPES = (
        ('writing_pre_analysis', 'Writing Pre-Analysis'),
        ('writing_task_1_analysis', 'Writing Task 1 Analysis'),
        ('writing_task_2_analysis', 'Writing Task 2 Analysis'),
        ('speaking_transcription', 'Speaking Transcription'),
        ('speaking_analysis', 'Speaking Analysis'),
        ('pronunciation_assessment', 'Pronunciation Assessment'),
        ('mock_report', 'Mock Report'),
        ('fallback_recheck', 'Fallback Recheck'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_usage_logs')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    provider = models.CharField(max_length=30)
    model = models.CharField(max_length=100)
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    audio_duration_seconds = models.FloatField(default=0)
    processing_time_ms = models.PositiveIntegerField(default=0)
    fallback_used = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='success')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI Usage Log"
        verbose_name_plural = "AI Usage Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.service_type} ({self.provider})"


class WritingSubmission(models.Model):
    """Foydalanuvchining Writing submission'i."""

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='writing_submissions')
    writing_task = models.ForeignKey('modules.WritingTask', on_delete=models.SET_NULL, blank=True, null=True)
    task_type = models.CharField(max_length=20, default='task_2')  # task_1, task_2
    content = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    quota_source = models.CharField(max_length=30, default='subscription')  # subscription, coin
    coin_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writing Submission"
        verbose_name_plural = "Writing Submissions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.task_type} ({self.status})"


class WritingAIFeedback(models.Model):
    """Writing AI tahlil natijasi."""

    submission = models.OneToOneField(WritingSubmission, on_delete=models.CASCADE, related_name='ai_feedback')
    provider = models.CharField(max_length=30)
    model = models.CharField(max_length=100)
    fallback_used = models.BooleanField(default=False)
    assessment_json = models.JSONField()
    estimated_overall_band = models.FloatField(blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    processing_time_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default='success')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Writing AI Feedback"
        verbose_name_plural = "Writing AI Feedbacks"

    def __str__(self):
        return f"Feedback for submission {self.submission_id} - Band {self.estimated_overall_band}"


class SpeakingAttempt(models.Model):
    """Speaking attempt."""

    STATUS_CHOICES = (
        ('recording', 'Recording'),
        ('uploaded', 'Uploaded'),
        ('transcribing', 'Transcribing'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='speaking_attempts')
    speaking_type = models.CharField(max_length=30, default='part_1')  # part_1, part_2, part_3, full_mock
    question_text = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='speaking_audio/%Y/%m/', blank=True, null=True)
    audio_duration_seconds = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recording')
    quota_source = models.CharField(max_length=30, default='subscription')
    coin_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Speaking Attempt"
        verbose_name_plural = "Speaking Attempts"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.speaking_type} ({self.status})"


class SpeakingTranscript(models.Model):
    """Speaking transcription natijasi."""

    attempt = models.OneToOneField(SpeakingAttempt, on_delete=models.CASCADE, related_name='transcript')
    provider = models.CharField(max_length=30)
    model = models.CharField(max_length=100)
    transcript = models.TextField()
    segments = models.JSONField(blank=True, null=True)
    language = models.CharField(max_length=10, default='en')
    confidence = models.FloatField(blank=True, null=True)
    fallback_used = models.BooleanField(default=False)
    processing_time_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Speaking Transcript"
        verbose_name_plural = "Speaking Transcripts"


class SpeakingAIFeedback(models.Model):
    """Speaking AI tahlil natijasi."""

    attempt = models.OneToOneField(SpeakingAttempt, on_delete=models.CASCADE, related_name='ai_feedback')
    provider = models.CharField(max_length=30)
    model = models.CharField(max_length=100)
    fallback_used = models.BooleanField(default=False)
    assessment_json = models.JSONField()
    estimated_overall_band = models.FloatField(blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    processing_time_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default='success')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Speaking AI Feedback"
        verbose_name_plural = "Speaking AI Feedbacks"
