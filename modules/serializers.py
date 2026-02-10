# from rest_framework import serializers
# from django.utils import timezone
# from .models import (
#     TestCategory, Test, Question, AnswerOption, MatchingItem,
#     TestAttempt, UserAnswer, TestResult, StudyMaterial
# )
#
#
# class TestCategorySerializer(serializers.ModelSerializer):
#     tests_count = serializers.SerializerMethodField()
#     average_difficulty = serializers.SerializerMethodField()
#
#     class Meta:
#         model = TestCategory
#         fields = ('id', 'name', 'description', 'icon', 'color', 'order',
#                  'is_active', 'tests_count', 'average_difficulty',
#                  'created_at', 'updated_at')
#         read_only_fields = ('created_at', 'updated_at')
#
#     def get_tests_count(self, obj):
#         return obj.tests.filter(is_active=True).count()
#
#     def get_average_difficulty(self, obj):
#         tests = obj.tests.filter(is_active=True)
#         if tests.exists():
#             return tests.aggregate(avg=models.Avg('difficulty'))['avg'] or 0
#         return 0
#
#
# class AnswerOptionSerializer(serializers.ModelSerializer):
#     is_correct = serializers.BooleanField(read_only=True)
#
#     class Meta:
#         model = AnswerOption
#         fields = ('id', 'text', 'is_correct', 'order', 'explanation')
#         read_only_fields = ('is_correct',)
#
#
# class MatchingItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MatchingItem
#         fields = ('id', 'left_text', 'right_text', 'order')
#
#
# class QuestionSerializer(serializers.ModelSerializer):
#     answer_options = AnswerOptionSerializer(many=True, read_only=True)
#     matching_items = MatchingItemSerializer(many=True, read_only=True)
#     question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
#     difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
#
#     class Meta:
#         model = Question
#         fields = ('id', 'test', 'question_text', 'question_type', 'question_type_display',
#                  'difficulty', 'difficulty_display', 'points', 'time_limit_seconds',
#                  'order', 'audio_file', 'image', 'passage_text', 'answer_options',
#                  'matching_items', 'correct_answer', 'explanation', 'hints',
#                  'created_at', 'updated_at')
#         read_only_fields = ('created_at', 'updated_at')
#
#
# class TestSerializer(serializers.ModelSerializer):
#     category_info = TestCategorySerializer(source='category', read_only=True)
#     questions_count = serializers.SerializerMethodField()
#     total_points = serializers.SerializerMethodField()
#     estimated_duration = serializers.SerializerMethodField()
#     difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
#
#     class Meta:
#         model = Test
#         fields = ('id', 'title', 'description', 'category', 'category_info',
#                  'difficulty', 'difficulty_display', 'time_limit_minutes',
#                  'questions_count', 'total_points', 'estimated_duration',
#                  'passing_score', 'is_active', 'is_premium', 'instructions',
#                  'created_at', 'updated_at')
#         read_only_fields = ('created_at', 'updated_at')
#
#     def get_questions_count(self, obj):
#         return obj.questions.count()
#
#     def get_total_points(self, obj):
#         return obj.questions.aggregate(total=models.Sum('points'))['total'] or 0
#
#     def get_estimated_duration(self, obj):
#         total_time = obj.questions.aggregate(
#             total=models.Sum('time_limit_seconds')
#         )['total'] or 0
#         return total_time // 60  # Convert to minutes
#
#
# class TestDetailSerializer(TestSerializer):
#     questions = QuestionSerializer(many=True, read_only=True)
#
#     class Meta(TestSerializer.Meta):
#         fields = TestSerializer.Meta.fields + ('questions',)
#
#
# class UserAnswerSerializer(serializers.ModelSerializer):
#     question_info = serializers.SerializerMethodField()
#     is_correct = serializers.BooleanField(read_only=True)
#     points_earned = serializers.FloatField(read_only=True)
#
#     class Meta:
#         model = UserAnswer
#         fields = ('id', 'attempt', 'question', 'question_info', 'selected_answer',
#                  'written_answer', 'matching_answers', 'is_correct', 'points_earned',
#                  'time_spent_seconds', 'answered_at')
#         read_only_fields = ('is_correct', 'points_earned', 'answered_at')
#
#     def get_question_info(self, obj):
#         return {
#             'id': obj.question.id,
#             'text': obj.question.question_text,
#             'type': obj.question.question_type,
#             'points': obj.question.points
#         }
#
#
# class TestResultSerializer(serializers.ModelSerializer):
#     band_score = serializers.FloatField(read_only=True)
#     performance_level = serializers.CharField(read_only=True)
#
#     class Meta:
#         model = TestResult
#         fields = ('id', 'attempt', 'total_score', 'max_score', 'percentage',
#                  'band_score', 'performance_level', 'feedback', 'recommendations',
#                  'created_at', 'updated_at')
#         read_only_fields = ('band_score', 'performance_level', 'created_at')
#
#
# class TestAttemptSerializer(serializers.ModelSerializer):
#     test_info = TestSerializer(source='test', read_only=True)
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     answers_count = serializers.SerializerMethodField()
#     correct_answers_count = serializers.SerializerMethodField()
#     result = TestResultSerializer(read_only=True)
#
#     class Meta:
#         model = TestAttempt
#         fields = ('id', 'user_email', 'test', 'test_info', 'status', 'status_display',
#                  'started_at', 'completed_at', 'time_spent_seconds', 'answers_count',
#                  'correct_answers_count', 'result', 'created_at', 'updated_at')
#         read_only_fields = ('user', 'started_at', 'completed_at', 'created_at')
#
#     def get_answers_count(self, obj):
#         return obj.answers.count()
#
#     def get_correct_answers_count(self, obj):
#         return obj.answers.filter(is_correct=True).count()
#
#
# class TestAttemptDetailSerializer(TestAttemptSerializer):
#     answers = UserAnswerSerializer(many=True, read_only=True)
#
#     class Meta(TestAttemptSerializer.Meta):
#         fields = TestAttemptSerializer.Meta.fields + ('answers',)
#
#
# class StudyMaterialSerializer(serializers.ModelSerializer):
#     category_info = TestCategorySerializer(source='category', read_only=True)
#     material_type_display = serializers.CharField(source='get_material_type_display', read_only=True)
#     difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
#
#     class Meta:
#         model = StudyMaterial
#         fields = ('id', 'title', 'description', 'category', 'category_info',
#                  'material_type', 'material_type_display', 'content', 'file',
#                  'video_url', 'difficulty', 'difficulty_display', 'estimated_time_minutes',
#                  'is_premium', 'order', 'tags', 'view_count', 'created_at', 'updated_at')
#         read_only_fields = ('view_count', 'created_at', 'updated_at')
#
#
# class StartTestSerializer(serializers.Serializer):
#     test_id = serializers.IntegerField(required=True)
#
#     def validate_test_id(self, value):
#         try:
#             test = Test.objects.get(id=value, is_active=True)
#             return value
#         except Test.DoesNotExist:
#             raise serializers.ValidationError("Test topilmadi yoki nofaol")
#
#
# class SubmitAnswerSerializer(serializers.Serializer):
#     question_id = serializers.IntegerField(required=True)
#     selected_answer = serializers.CharField(required=False, allow_blank=True)
#     written_answer = serializers.CharField(required=False, allow_blank=True)
#     matching_answers = serializers.JSONField(required=False)
#     time_spent_seconds = serializers.IntegerField(required=False, min_value=0)
#
#     def validate(self, attrs):
#         question_id = attrs.get('question_id')
#
#         try:
#             question = Question.objects.get(id=question_id)
#         except Question.DoesNotExist:
#             raise serializers.ValidationError("Savol topilmadi")
#
#         # Question type ga qarab validation
#         if question.question_type == 'multiple_choice':
#             if not attrs.get('selected_answer'):
#                 raise serializers.ValidationError("Multiple choice uchun javob tanlash shart")
#
#         elif question.question_type == 'true_false':
#             if attrs.get('selected_answer') not in ['true', 'false']:
#                 raise serializers.ValidationError("True/False uchun 'true' yoki 'false' tanlash shart")
#
#         elif question.question_type == 'short_answer':
#             if not attrs.get('written_answer'):
#                 raise serializers.ValidationError("Short answer uchun javob yozish shart")
#
#         elif question.question_type == 'essay':
#             if not attrs.get('written_answer'):
#                 raise serializers.ValidationError("Essay uchun javob yozish shart")
#
#         elif question.question_type == 'matching':
#             if not attrs.get('matching_answers'):
#                 raise serializers.ValidationError("Matching uchun javoblar juftligini kiritish shart")
#
#         return attrs
#
#
# class CompleteTestSerializer(serializers.Serializer):
#     pass  # No additional data needed
#
#
# class TestStatsSerializer(serializers.Serializer):
#     total_tests = serializers.IntegerField()
#     completed_tests = serializers.IntegerField()
#     average_score = serializers.FloatField()
#     best_score = serializers.FloatField()
#     total_time_spent = serializers.IntegerField()
#     average_band_score = serializers.FloatField()
#     category_stats = serializers.ListField()
#     recent_attempts = TestAttemptSerializer(many=True)
#
#
# class LeaderboardSerializer(serializers.Serializer):
#     user_email = serializers.EmailField()
#     total_score = serializers.FloatField()
#     tests_completed = serializers.IntegerField()
#     average_band = serializers.FloatField()
#     rank = serializers.IntegerField()
#
#
# class SearchTestSerializer(serializers.Serializer):
#     query = serializers.CharField(required=False, allow_blank=True)
#     category = serializers.IntegerField(required=False)
#     difficulty = serializers.ChoiceField(
#         choices=Test.DIFFICULTY_CHOICES,
#         required=False
#     )
#     is_premium = serializers.BooleanField(required=False)
#     min_time = serializers.IntegerField(required=False)
#     max_time = serializers.IntegerField(required=False)
#
#
# class RecommendationSerializer(serializers.Serializer):
#     test_id = serializers.IntegerField()
#     test_title = serializers.CharField()
#     reason = serializers.CharField()
#     confidence_score = serializers.FloatField()
#
#     class Meta:
#         ref_name = 'TestRecommendation'
#
#
# class ProgressAnalyticsSerializer(serializers.Serializer):
#     total_attempts = serializers.IntegerField()
#     average_score = serializers.FloatField()
#     improvement_rate = serializers.FloatField()
#     strong_areas = serializers.ListField()
#     weak_areas = serializers.ListField()
#     time_management = serializers.DictField()
#     accuracy_by_question_type = serializers.DictField()
#     progress_over_time = serializers.ListField()
#
#
# class BookmarkTestSerializer(serializers.Serializer):
#     test_id = serializers.IntegerField(required=True)
#
#     def validate_test_id(self, value):
#         try:
#             Test.objects.get(id=value, is_active=True)
#             return value
#         except Test.DoesNotExist:
#             raise serializers.ValidationError("Test topilmadi yoki nofaol")
#
#
# class TestReviewSerializer(serializers.ModelSerializer):
#     question_text = serializers.CharField(source='question.question_text', read_only=True)
#     correct_answer = serializers.CharField(source='question.correct_answer', read_only=True)
#     explanation = serializers.CharField(source='question.explanation', read_only=True)
#
#     class Meta:
#         model = UserAnswer
#         fields = ('id', 'question_text', 'selected_answer', 'written_answer',
#                  'matching_answers', 'correct_answer', 'explanation', 'is_correct',
#                  'points_earned', 'time_spent_seconds')
