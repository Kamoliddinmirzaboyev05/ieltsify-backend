from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class TestCategory(models.Model):
    """IELTS test kategoriyalari (Listening, Reading, Writing, Speaking)"""
    
    LISTENING = 'listening'
    READING = 'reading'
    WRITING = 'writing'
    SPEAKING = 'speaking'
    
    CATEGORY_CHOICES = (
        (LISTENING, 'Listening'),
        (READING, 'Reading'),
        (WRITING, 'Writing'),
        (SPEAKING, 'Speaking'),
    )
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Icon class or URL")
    color = models.CharField(max_length=20, default='#007bff', help_text="Category color")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        db_table = 'modules_test_category'
    
    def __str__(self):
        return self.get_name_display()


class Test(models.Model):
    """IELTS testlari"""
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, help_text="Test instructions for users")
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='tests')
    
    # Test turlari
    ACADEMIC = 'academic'
    GENERAL_TRAINING = 'general_training'
    
    TEST_TYPE_CHOICES = (
        (ACADEMIC, 'Academic'),
        (GENERAL_TRAINING, 'General Training'),
    )
    
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES, default=ACADEMIC)
    
    # Difficultyl darajasi
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    
    DIFFICULTY_CHOICES = (
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    )
    
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=MEDIUM)
    
    # Test haqida ma'lumotlar
    duration_minutes = models.PositiveIntegerField(help_text="Test duration in minutes")
    time_limit_minutes = models.PositiveIntegerField(help_text="Time limit for the test in minutes")
    total_questions = models.PositiveIntegerField(default=0)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=9.0)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=6.0, help_text="Minimum score to pass")
    
    # Narxlash
    is_free = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text="Premium testmi")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'modules_test'
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    
    def get_average_score(self):
        """Testning o'rtacha ballari"""
        attempts = self.attempts.filter(is_completed=True)
        if attempts.exists():
            return attempts.aggregate(models.Avg('score'))['score__avg']
        return 0
    
    def get_total_attempts(self):
        """Testni necha marta ishlaganliklari"""
        return self.attempts.filter(is_completed=True).count()


class Question(models.Model):
    """Test savollari"""
    
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    
    # Savol turlari
    MULTIPLE_CHOICE = 'multiple_choice'
    TRUE_FALSE = 'true_false'
    MATCHING = 'matching'
    FILL_BLANK = 'fill_blank'
    SHORT_ANSWER = 'short_answer'
    ESSAY = 'essay'
    RECORDING = 'recording'
    
    QUESTION_TYPE_CHOICES = (
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (TRUE_FALSE, 'True/False'),
        (MATCHING, 'Matching'),
        (FILL_BLANK, 'Fill in the Blank'),
        (SHORT_ANSWER, 'Short Answer'),
        (ESSAY, 'Essay'),
        (RECORDING, 'Recording'),
    )
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    
    # Savol matni
    question_text = models.TextField()
    passage_text = models.TextField(blank=True, help_text="Reading passage text for reading comprehension questions")
    question_image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    question_audio = models.FileField(upload_to='questions/audio/', blank=True, null=True)
    audio_file = models.FileField(upload_to='questions/audio_files/', blank=True, null=True, help_text="Audio file for the question")
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True, help_text="Additional image for the question")
    
    # Savol raqami va tartibi
    question_number = models.PositiveIntegerField(help_text="Question number in the test")
    section = models.CharField(max_length=100, blank=True, help_text="Section name for grouping")
    
    # Qiyinlik darajasi
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    
    DIFFICULTY_CHOICES = (
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    )
    
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=MEDIUM)
    
    # Ballar
    points = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    is_mandatory = models.BooleanField(default=False)
    time_limit_seconds = models.PositiveIntegerField(blank=True, null=True, help_text="Time limit for this question in seconds")
    order = models.PositiveIntegerField(default=0, help_text="Display order in test")
    
    # Qo'shimcha ma'lumotlar
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    hint = models.TextField(blank=True, help_text="Hint for the student")
    hints = models.JSONField(default=dict, blank=True, help_text="Multiple hints for the student")
    correct_answer = models.TextField(blank=True, help_text="Correct answer for the question")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['test', 'question_number']
        unique_together = ['test', 'question_number']
        db_table = 'modules_question'
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."


class AnswerOption(models.Model):
    """Multiple choice savollar uchun variantlar"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    option_text = models.TextField()
    text = models.TextField(blank=True, help_text="Additional text for the option")
    option_image = models.ImageField(upload_to='answers/images/', blank=True, null=True)
    
    # To'g'ri javob belgisi
    is_correct = models.BooleanField(default=False)
    
    # Variant harfi (A, B, C, D)
    option_label = models.CharField(max_length=1, blank=True)
    
    # Tartib
    order = models.PositiveIntegerField(default=0)
    
    # Qo'shimcha ma'lumotlar
    explanation = models.TextField(blank=True, help_text="Explanation for this answer option")
    
    class Meta:
        ordering = ['order']
        db_table = 'modules_answer_option'
    
    def __str__(self):
        return f"{self.option_label}: {self.option_text[:30]}..."


class MatchingItem(models.Model):
    """Matching savollar uchun itemlar"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='matching_items')
    
    # Chap tomondagi item
    left_item = models.CharField(max_length=500)
    left_item_image = models.ImageField(upload_to='matching/left/', blank=True, null=True)
    left_text = models.TextField(blank=True, help_text="Additional text for left item")
    
    # O'ng tomondagi item
    right_item = models.CharField(max_length=500)
    right_item_image = models.ImageField(upload_to='matching/right/', blank=True, null=True)
    right_text = models.TextField(blank=True, help_text="Additional text for right item")
    
    # To'g'ri juftlik
    is_correct_pair = models.BooleanField(default=False)
    
    # Tartib
    pair_order = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['pair_order']
        db_table = 'modules_matching_item'
    
    def __str__(self):
        return f"{self.left_item} <-> {self.right_item}"


class TestAttempt(models.Model):
    """Foydalanuvchining testni ishlashi"""
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    
    # Test holati
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'
    EXPIRED = 'expired'
    
    STATUS_CHOICES = (
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (ABANDONED, 'Abandoned'),
        (EXPIRED, 'Expired'),
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)
    
    # Vaqt
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_limit_minutes = models.PositiveIntegerField()
    time_spent_seconds = models.PositiveIntegerField(default=0, help_text="Testga sarflangan vaqt (soniyalar)")
    
    # Natijalar
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    correct_answers = models.PositiveIntegerField(default=0)
    total_answered = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        db_table = 'modules_test_attempt'
    
    def __str__(self):
        return f"{self.user.email} - {self.test.title} ({self.get_status_display()})"
    
    def is_completed(self):
        return self.status == self.COMPLETED
    
    def get_duration_minutes(self):
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() / 60)
        return 0
    
    def get_time_remaining_minutes(self):
        if self.status == self.COMPLETED:
            return 0
        
        elapsed = timezone.now() - self.started_at
        remaining = self.time_limit_minutes - int(elapsed.total_seconds() / 60)
        return max(0, remaining)


class UserAnswer(models.Model):
    """Foydalanuvchining javoblari"""
    
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Javob turlari
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.SET_NULL, blank=True, null=True)
    selected_answer = models.CharField(max_length=500, blank=True, help_text="Selected answer for the question")
    text_answer = models.TextField(blank=True)
    written_answer = models.TextField(blank=True, help_text="Written answer for the question")
    recorded_answer = models.FileField(upload_to='answers/recordings/', blank=True, null=True)
    
    # Matching javoblari
    matching_pairs = models.JSONField(default=dict, blank=True, help_text="For matching questions")
    matching_answers = models.JSONField(default=dict, blank=True, help_text="Matching answers for the question")
    
    # To'g'ri javobmi
    is_correct = models.BooleanField(blank=True, null=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Vaqt
    answered_at = models.DateTimeField(auto_now=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['attempt', 'question']
        db_table = 'modules_user_answer'
    
    def __str__(self):
        return f"Answer for Q{self.question.question_number} in {self.attempt.uuid}"


class TestResult(models.Model):
    """Test natijalari tahlili"""
    
    attempt = models.OneToOneField(TestAttempt, on_delete=models.CASCADE, related_name='result')
    
    # Bandlar bo'yicha natijalar
    listening_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    reading_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    writing_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    speaking_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # IELTS bandlari
    listening_band = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    reading_band = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    writing_band = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    speaking_band = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    
    # Umumiy IELTS balli
    overall_band = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Total score out of max score")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Maximum possible score")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Percentage score")
    
    # Tahlil
    strengths = models.TextField(blank=True, help_text="AI-generated strengths analysis")
    weaknesses = models.TextField(blank=True, help_text="AI-generated weaknesses analysis")
    recommendations = models.TextField(blank=True, help_text="AI-generated recommendations")
    feedback = models.TextField(blank=True, help_text="Overall feedback for the user")
    
    # Statistika
    percentile = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    rank = models.PositiveIntegerField(blank=True, null=True)
    total_participants = models.PositiveIntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules_test_result'
    
    def __str__(self):
        return f"Result for {self.attempt.user.email} - Overall: {self.overall_band}"


class StudyMaterial(models.Model):
    """O'quv materiallari"""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField(blank=True, help_text="Material content for text materials")
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='materials')
    
    # Material turi
    VIDEO = 'video'
    PDF = 'pdf'
    AUDIO = 'audio'
    TEXT = 'text'
    
    MATERIAL_TYPE_CHOICES = (
        (VIDEO, 'Video'),
        (PDF, 'PDF'),
        (AUDIO, 'Audio'),
        (TEXT, 'Text'),
    )
    
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE_CHOICES)
    
    # Fayl
    file = models.FileField(upload_to='materials/files/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="Video URL for video materials")
    
    # Narxlash
    is_free = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text="Premium material for VIP users")
    
    # Qiyinlik darajasi
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    
    DIFFICULTY_CHOICES = (
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    )
    
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=MEDIUM)
    estimated_time_minutes = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated time to complete the material")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    tags = models.JSONField(default=list, blank=True, help_text="Tags for the material")
    
    # Statistika
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'modules_study_material'
    
    def __str__(self):
        return self.title
