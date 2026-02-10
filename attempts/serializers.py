# from rest_framework import serializers
# from django.utils import timezone
# from .models import (
#     TestSession, SectionAttempt, QuestionResponse, ProgressTracker,
#     StudySession, ErrorLog, Recommendation
# )
#
#
# class TestSessionSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     duration = serializers.SerializerMethodField()
#     sections_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TestSession
#         fields = ('id', 'uuid', 'user_email', 'title', 'description', 'session_type',
#                  'session_type_display', 'status', 'status_display', 'started_at',
#                  'completed_at', 'total_duration_minutes', 'duration', 'sections_count',
#                  'total_score', 'total_percentage', 'overall_band', 'created_at', 'updated_at')
#         read_only_fields = ('uuid', 'user', 'started_at', 'completed_at', 'created_at')
#
#     def get_duration(self, obj):
#         minutes = obj.get_duration_minutes()
#         return f"{minutes} min" if minutes > 0 else "Not completed"
#
#     def get_sections_count(self, obj):
#         return obj.section_attempts.count()
#
#
# class SectionAttemptSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     test_title = serializers.CharField(source='test.title', read_only=True)
#     section_type_display = serializers.CharField(source='get_section_type_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     duration = serializers.SerializerMethodField()
#     accuracy = serializers.SerializerMethodField()
#     questions_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = SectionAttempt
#         fields = ('id', 'session', 'user_email', 'section_type', 'section_type_display',
#                  'test', 'test_title', 'status', 'status_display', 'started_at',
#                  'completed_at', 'time_limit_minutes', 'duration', 'score', 'percentage',
#                  'band_score', 'total_questions', 'correct_answers', 'skipped_questions',
#                  'accuracy', 'questions_count', 'coins_spent', 'created_at', 'updated_at')
#         read_only_fields = ('session', 'user', 'started_at', 'completed_at', 'created_at')
#
#     def get_duration(self, obj):
#         minutes = obj.get_duration_minutes()
#         return f"{minutes} min" if minutes > 0 else "Not completed"
#
#     def get_accuracy(self, obj):
#         accuracy = obj.get_accuracy()
#         return f"{accuracy:.1f}%" if accuracy > 0 else "0%"
#
#     def get_questions_count(self, obj):
#         return obj.question_responses.count()
#
#
# class QuestionResponseSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='section_attempt.user.email', read_only=True)
#     test_title = serializers.CharField(source='section_attempt.test.title', read_only=True)
#     question_number = serializers.SerializerMethodField()
#     question_text = serializers.CharField(source='question.question_text', read_only=True)
#     question_type = serializers.CharField(source='question.question_type', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     time_spent = serializers.SerializerMethodField()
#
#     class Meta:
#         model = QuestionResponse
#         fields = ('id', 'section_attempt', 'user_email', 'test_title', 'question',
#                  'question_number', 'question_text', 'question_type', 'status',
#                  'status_display', 'selected_answer', 'written_answer', 'matching_answers',
#                  'is_correct', 'points_earned', 'first_viewed_at', 'answered_at',
#                  'time_spent_seconds', 'time_spent', 'created_at', 'updated_at')
#         read_only_fields = ('section_attempt', 'question', 'first_viewed_at', 'answered_at', 'created_at')
#
#     def get_question_number(self, obj):
#         return f"Q{obj.question.question_number}"
#
#     def get_time_spent(self, obj):
#         minutes = obj.time_spent_seconds // 60
#         seconds = obj.time_spent_seconds % 60
#         return f"{minutes}:{seconds:02d}"
#
#
# class ProgressTrackerSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     category_display = serializers.CharField(source='category.name', read_only=True)
#     progress_percentage = serializers.FloatField(read_only=True)
#     streak_days = serializers.IntegerField(read_only=True)
#     days_to_target = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ProgressTracker
#         fields = ('id', 'user_email', 'category', 'category_display', 'total_tests_taken',
#                  'total_time_spent_minutes', 'average_score', 'best_score', 'current_band',
#                  'target_band', 'target_date', 'progress_percentage', 'streak_days',
#                  'last_activity_date', 'days_to_target', 'created_at', 'updated_at')
#         read_only_fields = ('user', 'created_at', 'updated_at')
#
#     def get_days_to_target(self, obj):
#         if obj.target_date:
#             days = (obj.target_date - timezone.now().date()).days
#             return max(0, days)
#         return None
#
#
# class StudySessionSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     material_title = serializers.CharField(source='material.title', read_only=True)
#     session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
#     duration = serializers.SerializerMethodField()
#
#     class Meta:
#         model = StudySession
#         fields = ('id', 'user_email', 'material', 'material_title', 'session_type',
#                  'session_type_display', 'started_at', 'completed_at', 'duration_minutes',
#                  'duration', 'completion_percentage', 'rating', 'notes', 'created_at', 'updated_at')
#         read_only_fields = ('user', 'started_at', 'completed_at', 'created_at')
#
#     def get_duration(self, obj):
#         if obj.duration_minutes > 0:
#             return f"{obj.duration_minutes} min"
#         return "Not completed"
#
#
# class ErrorLogSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     question_info = serializers.SerializerMethodField()
#     error_type_display = serializers.CharField(source='get_error_type_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#
#     class Meta:
#         model = ErrorLog
#         fields = ('id', 'user_email', 'question', 'question_info', 'error_type',
#                  'error_type_display', 'user_answer', 'correct_answer', 'explanation',
#                  'occurrence_count', 'first_occurrence', 'last_occurrence', 'status',
#                  'status_display', 'created_at', 'updated_at')
#         read_only_fields = ('user', 'question', 'first_occurrence', 'last_occurrence', 'created_at')
#
#     def get_question_info(self, obj):
#         return {
#             'id': obj.question.id,
#             'number': obj.question.question_number,
#             'text': obj.question.question_text[:100] + "..." if len(obj.question.question_text) > 100 else obj.question.question_text,
#             'type': obj.question.question_type
#         }
#
#
# class RecommendationSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
#     priority_display = serializers.CharField(source='get_priority_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#
#     class Meta:
#         model = Recommendation
#         ref_name = 'UserRecommendation'
#         fields = ('id', 'user_email', 'title', 'description', 'recommendation_type',
#                  'recommendation_type_display', 'target_skill', 'priority', 'priority_display',
#                  'status', 'status_display', 'expires_at', 'viewed_at', 'completed_at',
#                  'created_at', 'updated_at')
#         read_only_fields = ('user', 'created_at', 'updated_at')
#
#
# # Session management serializers
# class StartTestSessionSerializer(serializers.Serializer):
#     title = serializers.CharField(required=True)
#     description = serializers.CharField(required=False, allow_blank=True)
#     session_type = serializers.ChoiceField(choices=TestSession.SESSION_TYPE_CHOICES, default='full_test')
#     test_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
#
#     def validate(self, attrs):
#         if attrs.get('session_type') == 'custom' and not attrs.get('test_ids'):
#             raise serializers.ValidationError("Custom session uchun test IDs kerak")
#         return attrs
#
#
# class StartSectionSerializer(serializers.Serializer):
#     test_id = serializers.IntegerField(required=True)
#     section_type = serializers.ChoiceField(choices=SectionAttempt.SECTION_CHOICES, required=True)
#
#     def validate_test_id(self, value):
#         from modules.models import Test
#         try:
#             Test.objects.get(id=value, is_active=True)
#             return value
#         except Test.DoesNotExist:
#             raise serializers.ValidationError("Test topilmadi yoki nofaol")
#
#
# class SubmitResponseSerializer(serializers.Serializer):
#     question_id = serializers.IntegerField(required=True)
#     response = serializers.JSONField(required=False)
#     time_spent_seconds = serializers.IntegerField(required=False, min_value=0)
#
#     def validate_question_id(self, value):
#         from modules.models import Question
#         try:
#             Question.objects.get(id=value)
#             return value
#         except Question.DoesNotExist:
#             raise serializers.ValidationError("Savol topilmadi")
#
#
# class CompleteSectionSerializer(serializers.Serializer):
#     pass  # No additional data needed
#
#
# class CompleteSessionSerializer(serializers.Serializer):
#     pass  # No additional data needed
#
#
# # Analytics serializers
# class SessionAnalyticsSerializer(serializers.Serializer):
#     total_sessions = serializers.IntegerField()
#     completed_sessions = serializers.IntegerField()
#     average_score = serializers.FloatField()
#     average_band = serializers.FloatField()
#     total_time_spent = serializers.IntegerField()
#     improvement_rate = serializers.FloatField()
#     section_performance = serializers.DictField()
#     recent_sessions = TestSessionSerializer(many=True)
#
#
# class ProgressAnalyticsSerializer(serializers.Serializer):
#     overall_progress = serializers.DictField()
#     category_progress = serializers.ListField()
#     skill_strengths = serializers.ListField()
#     improvement_areas = serializers.ListField()
#     study_streak = serializers.IntegerField()
#     goal_tracking = serializers.DictField()
#
#
# class ErrorAnalysisSerializer(serializers.Serializer):
#     total_errors = serializers.IntegerField()
#     error_by_type = serializers.DictField()
#     error_by_category = serializers.DictField()
#     most_common_errors = serializers.ListField()
#     improvement_trends = serializers.DictField()
#
#
# class RecommendationEngineSerializer(serializers.Serializer):
#     personalized_tests = serializers.ListField()
#     study_materials = serializers.ListField()
#     skill_focus_areas = serializers.ListField()
#     estimated_improvement = serializers.DictField()
#
#
# # Study session serializers
# class StartStudySessionSerializer(serializers.Serializer):
#     material_id = serializers.IntegerField(required=True)
#     session_type = serializers.ChoiceField(choices=StudySession.SESSION_TYPE_CHOICES, default='study')
#
#     def validate_material_id(self, value):
#         from modules.models import StudyMaterial
#         try:
#             StudyMaterial.objects.get(id=value)
#             return value
#         except StudyMaterial.DoesNotExist:
#             raise serializers.ValidationError("Material topilmadi")
#
#
# class UpdateStudySessionSerializer(serializers.Serializer):
#     completion_percentage = serializers.IntegerField(min_value=0, max_value=100, required=False)
#     rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
#     notes = serializers.CharField(required=False, allow_blank=True)
#
#
# class StudySessionAnalyticsSerializer(serializers.Serializer):
#     total_sessions = serializers.IntegerField()
#     total_time_spent = serializers.IntegerField()
#     average_session_duration = serializers.FloatField()
#     preferred_materials = serializers.ListField()
#     study_patterns = serializers.DictField()
#     productivity_trends = serializers.ListField()
#
#
# # Progress tracking serializers
# class SetGoalSerializer(serializers.Serializer):
#     category_id = serializers.IntegerField(required=True)
#     target_band = serializers.FloatField(min_value=0.0, max_value=9.0, required=True)
#     target_date = serializers.DateField(required=True)
#
#     def validate_category_id(self, value):
#         from modules.models import TestCategory
#         try:
#             TestCategory.objects.get(id=value)
#             return value
#         except TestCategory.DoesNotExist:
#             raise serializers.ValidationError("Kategoriya topilmadi")
#
#
# class ProgressUpdateSerializer(serializers.Serializer):
#     category_id = serializers.IntegerField(required=False)
#     force_update = serializers.BooleanField(default=False)
#
#
# class LeaderboardSerializer(serializers.Serializer):
#     user_email = serializers.EmailField()
#     total_score = serializers.FloatField()
#     sessions_completed = serializers.IntegerField()
#     average_band = serializers.FloatField()
#     rank = serializers.IntegerField()
#     improvement = serializers.FloatField()
#
#
# class ComparisonSerializer(serializers.Serializer):
#     user_performance = serializers.DictField()
#     peer_average = serializers.DictField()
#     top_performers = serializers.DictField()
#     improvement_suggestions = serializers.ListField()
#
#
# class NotificationSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     type = serializers.CharField()
#     title = serializers.CharField()
#     message = serializers.CharField()
#     is_read = serializers.BooleanField()
#     created_at = serializers.DateTimeField()
#     expires_at = serializers.DateTimeField()
#
#
# class DashboardStatsSerializer(serializers.Serializer):
#     overview = serializers.DictField()
#     recent_activity = serializers.ListField()
#     upcoming_goals = serializers.ListField()
#     recommendations_count = serializers.IntegerField()
#     achievements = serializers.ListField()
