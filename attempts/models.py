from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class TestSession(models.Model):
    """Test sessiyasi - bir nechta testni birlashtirgan sessiya"""
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_sessions')
    
    # Sessiya turi
    PRACTICE = 'practice'
    EXAM = 'exam'
    REVIEW = 'review'
    
    SESSION_TYPE_CHOICES = (
        (PRACTICE, 'Practice'),
        (EXAM, 'Exam'),
        (REVIEW, 'Review'),
    )
    
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES, default=PRACTICE)
    
    # Sessiya haqida
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Vaqt
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    total_duration_minutes = models.PositiveIntegerField(default=0)
    
    # Natijalar
    total_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    overall_band = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    
    # Status
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'
    
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
        (ABANDONED, 'Abandoned'),
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        db_table = 'attempts_test_session'
    
    def __str__(self):
        return f"{self.user.email} - {self.title} ({self.get_status_display()})"
    
    def is_completed(self):
        return self.status == self.COMPLETED
    
    def get_duration_minutes(self):
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() / 60)
        return 0


class SectionAttempt(models.Model):
    """Test bo'limlari bo'yicha urinishlar (Listening, Reading, etc.)"""
    
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='section_attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='section_attempts')
    
    # Bo'lim turi
    LISTENING = 'listening'
    READING = 'reading'
    WRITING = 'writing'
    SPEAKING = 'speaking'
    
    SECTION_CHOICES = (
        (LISTENING, 'Listening'),
        (READING, 'Reading'),
        (WRITING, 'Writing'),
        (SPEAKING, 'Speaking'),
    )
    
    section_type = models.CharField(max_length=10, choices=SECTION_CHOICES)
    
    # Bo'lim haqida
    test = models.ForeignKey('modules.Test', on_delete=models.CASCADE, related_name='section_attempts')
    
    # Status
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'
    
    STATUS_CHOICES = (
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (ABANDONED, 'Abandoned'),
    )
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=IN_PROGRESS)
    
    # Vaqt
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_limit_minutes = models.PositiveIntegerField()
    
    # Natijalar
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    band_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    
    # Javoblar statistikasi
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    skipped_questions = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['session', 'section_type']
        db_table = 'attempts_section_attempt'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_section_type_display()} ({self.test.title})"
    
    def is_completed(self):
        return self.completed_at is not None
    
    def get_duration_minutes(self):
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() / 60)
        return 0
    
    def get_accuracy(self):
        if self.total_questions > 0:
            return (self.correct_answers / self.total_questions) * 100
        return 0


class QuestionResponse(models.Model):
    """Savolga javob berish vaqtini kuzatish"""
    
    section_attempt = models.ForeignKey(SectionAttempt, on_delete=models.CASCADE, related_name='question_responses')
    question = models.ForeignKey('modules.Question', on_delete=models.CASCADE)
    
    # Vaqt kuzatish
    first_viewed_at = models.DateTimeField(blank=True, null=True)
    answered_at = models.DateTimeField(blank=True, null=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    # Javob holati
    NOT_ANSWERED = 'not_answered'
    ANSWERED = 'answered'
    SKIPPED = 'skipped'
    FLAGGED = 'flagged'
    
    RESPONSE_STATUS_CHOICES = (
        (NOT_ANSWERED, 'Not Answered'),
        (ANSWERED, 'Answered'),
        (SKIPPED, 'Skipped'),
        (FLAGGED, 'Flagged'),
    )
    
    status = models.CharField(max_length=15, choices=RESPONSE_STATUS_CHOICES, default=NOT_ANSWERED)
    
    # Javob mazmuni
    selected_answer = models.CharField(max_length=500, blank=True, null=True, help_text="Multiple choice javobi")
    written_answer = models.TextField(blank=True, null=True, help_text="Written answer")
    matching_answers = models.JSONField(default=dict, blank=True, help_text="Matching answers")
    answer_data = models.JSONField(default=dict, blank=True, help_text="User's answer in JSON format")
    
    # To'g'ri javobmi
    is_correct = models.BooleanField(blank=True, null=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['section_attempt', 'question']
        db_table = 'attempts_question_response'
    
    def __str__(self):
        return f"Response for Q{self.question.question_number} in {self.section_attempt.test.title}"


class ProgressTracker(models.Model):
    """Foydalanuvchining progressini kuzatish"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_trackers')
    category = models.ForeignKey('modules.TestCategory', on_delete=models.CASCADE, related_name='progress_trackers')
    
    # Umumiy statistika
    total_tests_taken = models.PositiveIntegerField(default=0)
    total_time_spent_minutes = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    best_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    current_band = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    
    # Target
    target_band = models.DecimalField(max_digits=3, decimal_places=1, default=7.0)
    target_date = models.DateField(blank=True, null=True)
    
    # Progress
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category']
        db_table = 'attempts_progress_tracker'
    
    def __str__(self):
        return f"{self.user.email} - {self.category.get_name_display()} Progress"
    
    def update_progress(self):
        """Progress statistikasini yangilash"""
        from modules.models import TestAttempt
        
        attempts = TestAttempt.objects.filter(
            user=self.user,
            test__category=self.category,
            is_completed=True
        )
        
        if attempts.exists():
            self.total_tests_taken = attempts.count()
            self.average_score = attempts.aggregate(models.Avg('score'))['score__avg'] or 0
            self.best_score = attempts.aggregate(models.Max('score'))['score__max'] or 0
            self.total_time_spent_minutes = sum(a.get_duration_minutes() for a in attempts)
            
            # Oxirgi faoliyat
            last_attempt = attempts.order_by('-started_at').first()
            if last_attempt:
                self.last_activity_date = last_attempt.started_at
            
            # Progress foizini hisoblash
            if self.target_band > 0:
                self.progress_percentage = min(100, (self.average_score / self.target_band) * 100)
        
        self.save()


class StudySession(models.Model):
    """O'qish sessiyalari"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    material = models.ForeignKey('modules.StudyMaterial', on_delete=models.CASCADE, related_name='study_sessions')
    
    # Sessiya turi
    READING = 'reading'
    WATCHING = 'watching'
    PRACTICING = 'practicing'
    
    SESSION_TYPE_CHOICES = (
        (READING, 'Reading'),
        (WATCHING, 'Watching'),
        (PRACTICING, 'Practicing'),
    )
    
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES)
    
    # Vaqt
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    
    # Progress
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pages_read = models.PositiveIntegerField(default=0)
    minutes_watched = models.PositiveIntegerField(default=0)
    
    # Reyting
    rating = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(5)])
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        db_table = 'attempts_study_session'
    
    def __str__(self):
        return f"{self.user.email} - {self.material.title} ({self.get_session_type_display()})"
    
    def is_completed(self):
        return self.completed_at is not None


class ErrorLog(models.Model):
    """Xatoliklar jurnali"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='error_logs')
    question = models.ForeignKey('modules.Question', on_delete=models.CASCADE, related_name='error_logs')
    
    # Xatolik turi
    GRAMMAR = 'grammar'
    VOCABULARY = 'vocabulary'
    PRONUNCIATION = 'pronunciation'
    COMPREHENSION = 'comprehension'
    SPELLING = 'spelling'
    
    ERROR_TYPE_CHOICES = (
        (GRAMMAR, 'Grammar'),
        (VOCABULARY, 'Vocabulary'),
        (PRONUNCIATION, 'Pronunciation'),
        (COMPREHENSION, 'Comprehension'),
        (SPELLING, 'Spelling'),
    )
    
    error_type = models.CharField(max_length=15, choices=ERROR_TYPE_CHOICES)
    
    # Xatolik haqida
    user_answer = models.TextField(help_text="User's incorrect answer")
    correct_answer = models.TextField(help_text="Correct answer")
    explanation = models.TextField(blank=True, help_text="Explanation of the error")
    
    # Takrorlanish
    occurrence_count = models.PositiveIntegerField(default=1)
    first_occurrence = models.DateTimeField(auto_now_add=True)
    last_occurrence = models.DateTimeField(auto_now=True)
    
    # Status
    RESOLVED = 'resolved'
    PENDING = 'pending'
    
    STATUS_CHOICES = (
        (RESOLVED, 'Resolved'),
        (PENDING, 'Pending'),
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_occurrence']
        db_table = 'attempts_error_log'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_error_type_display()} Error"


class Recommendation(models.Model):
    """AI tavsiyalari"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    
    # Tavsiya turi
    STUDY_MATERIAL = 'study_material'
    PRACTICE_TEST = 'practice_test'
    VIDEO_LESSON = 'video_lesson'
    EXERCISE = 'exercise'
    
    RECOMMENDATION_TYPE_CHOICES = (
        (STUDY_MATERIAL, 'Study Material'),
        (PRACTICE_TEST, 'Practice Test'),
        (VIDEO_LESSON, 'Video Lesson'),
        (EXERCISE, 'Exercise'),
    )
    
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    
    # Tavsiya mazmuni
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_skill = models.CharField(max_length=50, help_text="Target skill to improve")
    
    # Bog'liq resurslar
    related_material = models.ForeignKey('modules.StudyMaterial', on_delete=models.SET_NULL, blank=True, null=True)
    related_test = models.ForeignKey('modules.Test', on_delete=models.SET_NULL, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    
    # Prioritet va status
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    )
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    
    # Status
    PENDING = 'pending'
    VIEWED = 'viewed'
    COMPLETED = 'completed'
    DISMISSED = 'dismissed'
    
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (VIEWED, 'Viewed'),
        (COMPLETED, 'Completed'),
        (DISMISSED, 'Dismissed'),
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    
    # Vaqt
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text="Tavsiyaning amal qilish muddati")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        db_table = 'attempts_recommendation'
    
    def __str__(self):
        return f"{self.user.email} - {self.title} ({self.get_status_display()})"
