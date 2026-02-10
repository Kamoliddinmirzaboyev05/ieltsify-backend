# from rest_framework import status, permissions, generics
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# from django.utils.decorators import method_decorator
# from django.db.models import Count, Sum, Avg, Q
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from .serializers import (
#     TestCategorySerializer, TestSerializer, TestDetailSerializer,
#     TestAttemptSerializer, TestAttemptDetailSerializer, UserAnswerSerializer,
#     TestResultSerializer, StudyMaterialSerializer, StartTestSerializer,
#     SubmitAnswerSerializer, CompleteTestSerializer, TestStatsSerializer,
#     LeaderboardSerializer, SearchTestSerializer, RecommendationSerializer,
#     ProgressAnalyticsSerializer, BookmarkTestSerializer, TestReviewSerializer
# )
# from .models import TestCategory, Test, TestAttempt
# from .services import TestService, StudyMaterialService, TestAnalyticsService
# from accounts.permissions import IsAdminUser, IsOwnerOrAdmin
#
#
# class TestCategoryListView(generics.ListAPIView):
#     """Test kategoriyalari ro'yxati"""
#     serializer_class = TestCategorySerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         return TestService.get_categories()
#
#     @swagger_auto_schema(
#         operation_description="IELTS test kategoriyalari ro'yxati",
#         responses={200: TestCategorySerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class TestListView(generics.ListAPIView):
#     """Testlar ro'yxati"""
#     serializer_class = TestSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         category_id = self.request.GET.get('category')
#         filters = {
#             'query': self.request.GET.get('query'),
#             'difficulty': self.request.GET.get('difficulty'),
#             'is_premium': self.request.GET.get('is_premium'),
#             'min_time': self.request.GET.get('min_time'),
#             'max_time': self.request.GET.get('max_time')
#         }
#
#         # Convert string to boolean for is_premium
#         if filters['is_premium'] is not None:
#             filters['is_premium'] = filters['is_premium'].lower() == 'true'
#
#         # Remove None values
#         filters = {k: v for k, v in filters.items() if v is not None}
#
#         return TestService.get_tests_by_category(category_id, filters)
#
#     @swagger_auto_schema(
#         operation_description="Testlar ro'yxati (filterlar bilan)",
#         manual_parameters=[
#             openapi.Parameter('category', openapi.IN_QUERY, description="Kategoriya ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('query', openapi.IN_QUERY, description="Qidiruv so'zi", type=openapi.TYPE_STRING),
#             openapi.Parameter('difficulty', openapi.IN_QUERY, description="Qiyinlik darajasi", type=openapi.TYPE_STRING, enum=['beginner', 'intermediate', 'advanced']),
#             openapi.Parameter('is_premium', openapi.IN_QUERY, description="Premium testlar", type=openapi.TYPE_BOOLEAN),
#             openapi.Parameter('min_time', openapi.IN_QUERY, description="Minimal vaqt (daqiqa)", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('max_time', openapi.IN_QUERY, description="Maksimal vaqt (daqiqa)", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: TestSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class TestDetailView(generics.RetrieveAPIView):
#     """Test detaili"""
#     serializer_class = TestDetailSerializer
#     permission_classes = [permissions.AllowAny]
#     lookup_field = 'id'
#
#     def get_object(self):
#         test_id = self.kwargs['id']
#         return TestService.get_test_detail(test_id)
#
#     @swagger_auto_schema(
#         operation_description="Test detail ma'lumotlari (savollar bilan birga)",
#         responses={200: TestDetailSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         test = self.get_object()
#         if not test:
#             return Response({
#                 'error': 'Test topilmadi'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = self.get_serializer(test)
#         return Response(serializer.data)
#
#
# class StartTestView(APIView):
#     """Testni boshlash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Testni boshlash",
#         request_body=StartTestSerializer,
#         responses={201: TestAttemptSerializer}
#     )
#     def post(self, request):
#         serializer = StartTestSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 test_id = serializer.validated_data['test_id']
#                 attempt = TestService.start_test(request.user, test_id)
#
#                 return Response({
#                     'message': 'Test muvaffaqiyatli boshlandi',
#                     'attempt': TestAttemptSerializer(attempt).data
#                 }, status=status.HTTP_201_CREATED)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Testni boshlashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class SubmitAnswerView(APIView):
#     """Javob yuborish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Test savoliga javob yuborish",
#         request_body=SubmitAnswerSerializer,
#         responses={200: UserAnswerSerializer}
#     )
#     def post(self, request):
#         serializer = SubmitAnswerSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 # Attempt ID ni URL dan olish
#                 attempt_id = request.GET.get('attempt_id')
#                 if not attempt_id:
#                     return Response({
#                         'error': 'Attempt ID kerak'
#                     }, status=status.HTTP_400_BAD_REQUEST)
#
#                 answer_data = serializer.validated_data
#                 answer = TestService.submit_answer(
#                     request.user,
#                     attempt_id,
#                     answer_data
#                 )
#
#                 return Response({
#                     'message': 'Javob muvaffaqiyatli yuborildi',
#                     'answer': UserAnswerSerializer(answer).data
#                 }, status=status.HTTP_200_OK)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Javob yuborishda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class CompleteTestView(APIView):
#     """Testni tugatish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Testni tugatish va natijalarni olish",
#         manual_parameters=[
#             openapi.Parameter('attempt_id', openapi.IN_QUERY, description="Attempt ID", type=openapi.TYPE_INTEGER, required=True)
#         ],
#         responses={200: TestAttemptDetailSerializer}
#     )
#     def post(self, request):
#         attempt_id = request.GET.get('attempt_id')
#         if not attempt_id:
#             return Response({
#                 'error': 'Attempt ID kerak'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             attempt, result = TestService.complete_test(request.user, attempt_id)
#
#             return Response({
#                 'message': 'Test muvaffaqiyatli tugatildi',
#                 'attempt': TestAttemptDetailSerializer(attempt).data,
#                 'result': TestResultSerializer(result).data
#             }, status=status.HTTP_200_OK)
#
#         except ValueError as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 'error': 'Testni tugatishda xatolik',
#                 'detail': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class UserTestAttemptsView(generics.ListAPIView):
#     """Foydalanuvchi test urinishlari"""
#     serializer_class = TestAttemptSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         test_id = self.request.GET.get('test_id')
#         status_filter = self.request.GET.get('status')
#         return TestService.get_user_attempts(self.request.user, test_id, status_filter)
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining test urinishlari ro'yxati",
#         manual_parameters=[
#             openapi.Parameter('test_id', openapi.IN_QUERY, description="Test ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('status', openapi.IN_QUERY, description="Status", type=openapi.TYPE_STRING, enum=['in_progress', 'completed', 'abandoned']),
#         ],
#         responses={200: TestAttemptSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class TestAttemptDetailView(generics.RetrieveAPIView):
#     """Test urinishi detaili"""
#     serializer_class = TestAttemptDetailSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'id'
#
#     def get_queryset(self):
#         return TestService.get_user_attempts(self.request.user)
#
#     @swagger_auto_schema(
#         operation_description="Test urinishi detail ma'lumotlari",
#         responses={200: TestAttemptDetailSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class TestStatsView(APIView):
#     """Foydalanuvchi test statistikasi"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining test statistikasi",
#         responses={200: TestStatsSerializer}
#     )
#     def get(self, request):
#         stats = TestService.get_test_stats(request.user)
#
#         # Recent attempts
#         recent_attempts = TestService.get_user_attempts(
#             request.user,
#             status='completed'
#         )[:5]
#
#         data = {
#             **stats,
#             'recent_attempts': TestAttemptSerializer(recent_attempts, many=True).data
#         }
#
#         return Response({
#             'success': True,
#             'data': data
#         })
#
#
# class LeaderboardView(APIView):
#     """Leaderboard"""
#     permission_classes = [permissions.AllowAny]
#
#     @swagger_auto_schema(
#         operation_description="Testlar bo'yicha leaderboard",
#         manual_parameters=[
#             openapi.Parameter('category', openapi.IN_QUERY, description="Kategoriya ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('limit', openapi.IN_QUERY, description="Natijalar soni", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: LeaderboardSerializer(many=True)}
#     )
#     def get(self, request):
#         category_id = request.GET.get('category')
#         limit = int(request.GET.get('limit', 10))
#
#         leaderboard = TestService.get_leaderboard(category_id, limit)
#
#         return Response({
#             'success': True,
#             'data': leaderboard
#         })
#
#
# class RecommendationsView(APIView):
#     """Personalized tavsiyalar"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchi uchun personalized test tavsiyalari",
#         manual_parameters=[
#             openapi.Parameter('limit', openapi.IN_QUERY, description="Tavsiyalar soni", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: RecommendationSerializer(many=True)}
#     )
#     def get(self, request):
#         limit = int(request.GET.get('limit', 5))
#         recommendations = TestService.get_recommendations(request.user, limit)
#
#         return Response({
#             'success': True,
#             'data': TestSerializer(recommendations, many=True).data
#         })
#
#
# class StudyMaterialListView(generics.ListAPIView):
#     """Study materiallar ro'yxati"""
#     serializer_class = StudyMaterialSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         category_id = self.request.GET.get('category')
#         filters = {
#             'material_type': self.request.GET.get('material_type'),
#             'difficulty': self.request.GET.get('difficulty'),
#             'is_premium': self.request.GET.get('is_premium'),
#             'query': self.request.GET.get('query')
#         }
#
#         # Convert string to boolean for is_premium
#         if filters['is_premium'] is not None:
#             filters['is_premium'] = filters['is_premium'].lower() == 'true'
#
#         # Remove None values
#         filters = {k: v for k, v in filters.items() if v is not None}
#
#         return StudyMaterialService.get_materials(category_id, filters)
#
#     @swagger_auto_schema(
#         operation_description="Study materiallar ro'yxati",
#         manual_parameters=[
#             openapi.Parameter('category', openapi.IN_QUERY, description="Kategoriya ID", type=openapi.TYPE_INTEGER),
#             openapi.Parameter('material_type', openapi.IN_QUERY, description="Material turi", type=openapi.TYPE_STRING),
#             openapi.Parameter('difficulty', openapi.IN_QUERY, description="Qiyinlik darajasi", type=openapi.TYPE_STRING),
#             openapi.Parameter('is_premium', openapi.IN_QUERY, description="Premium materiallar", type=openapi.TYPE_BOOLEAN),
#             openapi.Parameter('query', openapi.IN_QUERY, description="Qidiruv so'zi", type=openapi.TYPE_STRING),
#         ],
#         responses={200: StudyMaterialSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class StudyMaterialDetailView(generics.RetrieveAPIView):
#     """Study material detaili"""
#     serializer_class = StudyMaterialSerializer
#     permission_classes = [permissions.AllowAny]
#     lookup_field = 'id'
#
#     def get_object(self):
#         material_id = self.kwargs['id']
#         return StudyMaterialService.get_material_detail(material_id)
#
#     @swagger_auto_schema(
#         operation_description="Study material detail ma'lumotlari",
#         responses={200: StudyMaterialSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         material = self.get_object()
#         if not material:
#             return Response({
#                 'error': 'Material topilmadi'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = self.get_serializer(material)
#         return Response(serializer.data)
#
#
# class AccessMaterialView(APIView):
#     """Study materialga kirish (premium uchun tekshirish)"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Study materialga kirish (usage ni hisobga olgan holda)",
#         manual_parameters=[
#             openapi.Parameter('material_id', openapi.IN_QUERY, description="Material ID", type=openapi.TYPE_INTEGER, required=True)
#         ],
#         responses={200: StudyMaterialSerializer}
#     )
#     def post(self, request):
#         material_id = request.GET.get('material_id')
#         if not material_id:
#             return Response({
#                 'error': 'Material ID kerak'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             material = StudyMaterialService.access_material(request.user, material_id)
#
#             return Response({
#                 'message': 'Materialga muvaffaqiyatli kirildi',
#                 'material': StudyMaterialSerializer(material).data
#             }, status=status.HTTP_200_OK)
#
#         except ValueError as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 'error': 'Materialga kirishda xatolik',
#                 'detail': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class ProgressAnalyticsView(APIView):
#     """Foydalanuvchi progress analytics"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining progress analyticsi",
#         manual_parameters=[
#             openapi.Parameter('days', openapi.IN_QUERY, description="Qancha kunlik ma'lumot", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: ProgressAnalyticsSerializer}
#     )
#     def get(self, request):
#         days = int(request.GET.get('days', 30))
#         analytics = TestAnalyticsService.get_user_analytics(request.user, days)
#
#         return Response({
#             'success': True,
#             'data': analytics
#         })
#
#
# class TestReviewView(generics.RetrieveAPIView):
#     """Testni ko'rib chiqish (javoblar bilan birga)"""
#     serializer_class = TestReviewSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'id'
#
#     def get_queryset(self):
#         return TestService.get_user_attempts(
#             self.request.user,
#             status='completed'
#         )
#
#     @swagger_auto_schema(
#         operation_description="Testni ko'rib chiqish (to'g'ri javoblar va izohlar bilan)",
#         responses={200: TestReviewSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         attempt = self.get_object()
#         if not attempt:
#             return Response({
#                 'error': 'Test attempt topilmadi'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         # Barcha javoblarni olish
#         answers = attempt.answers.all()
#         serializer = TestReviewSerializer(answers, many=True)
#
#         return Response({
#             'success': True,
#             'data': {
#                 'attempt': TestAttemptSerializer(attempt).data,
#                 'answers': serializer.data
#             }
#         })
#
#
# # Admin views
# class AdminTestCategoryListCreateView(generics.ListCreateAPIView):
#     """Test kategoriyalari (Admin)"""
#     serializer_class = TestCategorySerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = TestCategory.objects.all()
#
#     @swagger_auto_schema(
#         operation_description="Test kategoriyalar ro'yxati (Admin)",
#         responses={200: TestCategorySerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#     @swagger_auto_schema(
#         operation_description="Yangi test kategoriyasi yaratish (Admin)",
#         request_body=TestCategorySerializer,
#         responses={201: TestCategorySerializer}
#     )
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)
#
#
# class AdminTestDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """Test detail (Admin)"""
#     serializer_class = TestDetailSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = Test.objects.all()
#     lookup_field = 'id'
#
#     @swagger_auto_schema(
#         operation_description="Test detail ma'lumotlari (Admin)",
#         responses={200: TestDetailSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#     @swagger_auto_schema(
#         operation_description="Testni yangilash (Admin)",
#         request_body=TestDetailSerializer,
#         responses={200: TestDetailSerializer}
#     )
#     def patch(self, request, *args, **kwargs):
#         return super().partial_update(request, *args, **kwargs)
#
#
# class AdminAllAttemptsView(generics.ListAPIView):
#     """Barcha test urinishlari (Admin)"""
#     serializer_class = TestAttemptSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = TestAttempt.objects.all().order_by('-created_at')
#
#     @swagger_auto_schema(
#         operation_description="Barcha test urinishlari ro'yxati (Admin)",
#         responses={200: TestAttemptSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
