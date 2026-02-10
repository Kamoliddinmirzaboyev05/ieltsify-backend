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
#     TestSessionSerializer, SectionAttemptSerializer, QuestionResponseSerializer,
#     ProgressTrackerSerializer, StudySessionSerializer, ErrorLogSerializer,
#     RecommendationSerializer, StartTestSessionSerializer, StartSectionSerializer,
#     SubmitResponseSerializer, CompleteSectionSerializer, CompleteSessionSerializer,
#     SessionAnalyticsSerializer, ProgressAnalyticsSerializer, ErrorAnalysisSerializer,
#     RecommendationEngineSerializer, StartStudySessionSerializer,
#     UpdateStudySessionSerializer, StudySessionAnalyticsSerializer,
#     SetGoalSerializer, ProgressUpdateSerializer, LeaderboardSerializer,
#     ComparisonSerializer, DashboardStatsSerializer
# )
# from .models import ProgressTracker, ErrorLog, TestSession
# from .services import (
#     TestSessionService, StudySessionService, ErrorAnalysisService,
#     RecommendationService, DashboardService
# )
# from accounts.permissions import IsAdminUser, IsOwnerOrAdmin
#
#
# class TestSessionListView(generics.ListAPIView):
#     """Test sessiyalari ro'yxati"""
#     serializer_class = TestSessionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         status_filter = self.request.GET.get('status')
#         limit = int(self.request.GET.get('limit', 20))
#         return TestSessionService.get_user_sessions(self.request.user, status_filter, limit)
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining test sessiyalari ro'yxati",
#         manual_parameters=[
#             openapi.Parameter('status', openapi.IN_QUERY, description="Status", type=openapi.TYPE_STRING, enum=['active', 'completed', 'abandoned']),
#             openapi.Parameter('limit', openapi.IN_QUERY, description="Natijalar soni", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: TestSessionSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class StartTestSessionView(APIView):
#     """Test sessiyasini boshlash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Yangi test sessiyasini boshlash",
#         request_body=StartTestSessionSerializer,
#         responses={201: TestSessionSerializer}
#     )
#     def post(self, request):
#         serializer = StartTestSessionSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 session = TestSessionService.start_session(
#                     request.user,
#                     serializer.validated_data
#                 )
#
#                 return Response({
#                     'message': 'Test sessiyasi muvaffaqiyatli boshlandi',
#                     'session': TestSessionSerializer(session).data
#                 }, status=status.HTTP_201_CREATED)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Test sessiyasini boshlashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class StartSectionView(APIView):
#     """Test bo'limini boshlash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Test bo'limini boshlash",
#         request_body=StartSectionSerializer,
#         responses={201: SectionAttemptSerializer}
#     )
#     def post(self, request):
#         serializer = StartSectionSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 session_id = request.GET.get('session_id')
#                 if not session_id:
#                     return Response({
#                         'error': 'Session ID kerak'
#                     }, status=status.HTTP_400_BAD_REQUEST)
#
#                 section = TestSessionService.start_section(
#                     request.user,
#                     session_id,
#                     serializer.validated_data
#                 )
#
#                 return Response({
#                     'message': 'Bo\'lim muvaffaqiyatli boshlandi',
#                     'section': SectionAttemptSerializer(section).data
#                 }, status=status.HTTP_201_CREATED)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Bo\'limni boshlashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class SubmitResponseView(APIView):
#     """Javob yuborish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Test savoliga javob yuborish",
#         request_body=SubmitResponseSerializer,
#         responses={200: QuestionResponseSerializer}
#     )
#     def post(self, request):
#         serializer = SubmitResponseSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 section_id = request.GET.get('section_id')
#                 if not section_id:
#                     return Response({
#                         'error': 'Section ID kerak'
#                     }, status=status.HTTP_400_BAD_REQUEST)
#
#                 response = TestSessionService.submit_response(
#                     request.user,
#                     section_id,
#                     serializer.validated_data
#                 )
#
#                 return Response({
#                     'message': 'Javob muvaffaqiyatli yuborildi',
#                     'response': QuestionResponseSerializer(response).data
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
# class CompleteSectionView(APIView):
#     """Bo'limni tugatish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Test bo'limini tugatish",
#         request_body=CompleteSectionSerializer,
#         manual_parameters=[
#             openapi.Parameter('section_id', openapi.IN_QUERY, description="Section ID", type=openapi.TYPE_INTEGER, required=True)
#         ],
#         responses={200: SectionAttemptSerializer}
#     )
#     def post(self, request):
#         section_id = request.GET.get('section_id')
#         if not section_id:
#             return Response({
#                 'error': 'Section ID kerak'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             section = TestSessionService.complete_section(request.user, section_id)
#
#             return Response({
#                 'message': 'Bo\'lim muvaffaqiyatli tugatildi',
#                 'section': SectionAttemptSerializer(section).data
#             }, status=status.HTTP_200_OK)
#
#         except ValueError as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 'error': 'Bo\'limni tugatishda xatolik',
#                 'detail': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class CompleteSessionView(APIView):
#     """Test sessiyasini tugatish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Test sessiyasini tugatish",
#         request_body=CompleteSessionSerializer,
#         manual_parameters=[
#             openapi.Parameter('session_id', openapi.IN_QUERY, description="Session ID", type=openapi.TYPE_INTEGER, required=True)
#         ],
#         responses={200: TestSessionSerializer}
#     )
#     def post(self, request):
#         session_id = request.GET.get('session_id')
#         if not session_id:
#             return Response({
#                 'error': 'Session ID kerak'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             session = TestSessionService.complete_session(request.user, session_id)
#
#             return Response({
#                 'message': 'Test sessiyasi muvaffaqiyatli tugatildi',
#                 'session': TestSessionSerializer(session).data
#             }, status=status.HTTP_200_OK)
#
#         except ValueError as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 'error': 'Test sessiyasini tugatishda xatolik',
#                 'detail': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class SessionAnalyticsView(APIView):
#     """Sessiya analytics"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Test sessiyalari analyticsi",
#         manual_parameters=[
#             openapi.Parameter('days', openapi.IN_QUERY, description="Qancha kunlik ma'lumot", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: SessionAnalyticsSerializer}
#     )
#     def get(self, request):
#         days = int(request.GET.get('days', 30))
#         analytics = TestSessionService.get_session_analytics(request.user, days)
#
#         return Response({
#             'success': True,
#             'data': analytics
#         })
#
#
# class ProgressTrackerListView(generics.ListAPIView):
#     """Progress trackerlar ro'yxati"""
#     serializer_class = ProgressTrackerSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return ProgressTracker.objects.filter(user=self.request.user).order_by('-last_activity_date')
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchi progress trackerlari",
#         responses={200: ProgressTrackerSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class SetGoalView(APIView):
#     """Yangi maqsad qo'yish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Yangi o'rganish maqsadi qo'yish",
#         request_body=SetGoalSerializer,
#         responses={201: ProgressTrackerSerializer}
#     )
#     def post(self, request):
#         serializer = SetGoalSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 category_id = serializer.validated_data['category_id']
#                 target_band = serializer.validated_data['target_band']
#                 target_date = serializer.validated_data['target_date']
#
#                 from modules.models import TestCategory
#                 category = TestCategory.objects.get(id=category_id)
#
#                 tracker, created = ProgressTracker.objects.update_or_create(
#                     user=request.user,
#                     category=category,
#                     defaults={
#                         'target_band': target_band,
#                         'target_date': target_date
#                     }
#                 )
#
#                 if not created:
#                     tracker.target_band = target_band
#                     tracker.target_date = target_date
#                     tracker.save()
#
#                 return Response({
#                     'message': 'Maqsad muvaffaqiyatli qo\'yildi',
#                     'goal': ProgressTrackerSerializer(tracker).data
#                 }, status=status.HTTP_201_CREATED)
#
#             except TestCategory.DoesNotExist:
#                 return Response({
#                     'error': 'Kategoriya topilmadi'
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Maqsad qo\'yishda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UpdateProgressView(APIView):
#     """Progressni yangilash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Progressni yangilash",
#         request_body=ProgressUpdateSerializer,
#         responses={200: ProgressTrackerSerializer(many=True)}
#     )
#     def post(self, request):
#         serializer = ProgressUpdateSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 category_id = serializer.validated_data.get('category_id')
#                 force_update = serializer.validated_data.get('force_update', False)
#
#                 trackers = ProgressTracker.objects.filter(user=request.user)
#                 if category_id:
#                     from modules.models import TestCategory
#                     category = TestCategory.objects.get(id=category_id)
#                     trackers = trackers.filter(category=category)
#
#                 for tracker in trackers:
#                     if force_update or tracker.should_update():
#                         tracker.update_progress()
#
#                 return Response({
#                     'message': 'Progress muvaffaqiyatli yangilandi',
#                     'trackers': ProgressTrackerSerializer(trackers, many=True).data
#                 }, status=status.HTTP_200_OK)
#
#             except TestCategory.DoesNotExist:
#                 return Response({
#                     'error': 'Kategoriya topilmadi'
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Progressni yangilashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class StudySessionListView(generics.ListAPIView):
#     """Study sessiyalari ro'yxati"""
#     serializer_class = StudySessionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         limit = int(self.request.GET.get('limit', 20))
#         return StudySessionService.get_user_study_sessions(self.request.user, limit)
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining study sessiyalari",
#         manual_parameters=[
#             openapi.Parameter('limit', openapi.IN_QUERY, description="Natijalar soni", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: StudySessionSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class StartStudySessionView(APIView):
#     """Study sessiyasini boshlash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Study sessiyasini boshlash",
#         request_body=StartStudySessionSerializer,
#         responses={201: StudySessionSerializer}
#     )
#     def post(self, request):
#         serializer = StartStudySessionSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 session = StudySessionService.start_study_session(
#                     request.user,
#                     serializer.validated_data
#                 )
#
#                 return Response({
#                     'message': 'Study sessiyasi muvaffaqiyatli boshlandi',
#                     'session': StudySessionSerializer(session).data
#                 }, status=status.HTTP_201_CREATED)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Study sessiyasini boshlashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UpdateStudySessionView(APIView):
#     """Study sessiyasini yangilash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Study sessiyasini yangilash",
#         request_body=UpdateStudySessionSerializer,
#         manual_parameters=[
#             openapi.Parameter('session_id', openapi.IN_QUERY, description="Session ID", type=openapi.TYPE_INTEGER, required=True)
#         ],
#         responses={200: StudySessionSerializer}
#     )
#     def patch(self, request):
#         session_id = request.GET.get('session_id')
#         if not session_id:
#             return Response({
#                 'error': 'Session ID kerak'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         serializer = UpdateStudySessionSerializer(data=request.data)
#
#         if serializer.is_valid():
#             try:
#                 session = StudySessionService.update_study_session(
#                     request.user,
#                     session_id,
#                     serializer.validated_data
#                 )
#
#                 return Response({
#                     'message': 'Study sessiyasi muvaffaqiyatli yangilandi',
#                     'session': StudySessionSerializer(session).data
#                 }, status=status.HTTP_200_OK)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Study sessiyasini yangilashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class StudyAnalyticsView(APIView):
#     """Study analytics"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Study sessiyalari analyticsi",
#         manual_parameters=[
#             openapi.Parameter('days', openapi.IN_QUERY, description="Qancha kunlik ma'lumot", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: StudySessionAnalyticsSerializer}
#     )
#     def get(self, request):
#         days = int(request.GET.get('days', 30))
#         analytics = StudySessionService.get_study_analytics(request.user, days)
#
#         return Response({
#             'success': True,
#             'data': analytics
#         })
#
#
# class ErrorLogListView(generics.ListAPIView):
#     """Xatoliklar ro'yxati"""
#     serializer_class = ErrorLogSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return ErrorLog.objects.filter(user=self.request.user).order_by('-last_occurrence')
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining xatoliklari ro'yxati",
#         responses={200: ErrorLogSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class ErrorAnalysisView(APIView):
#     """Xatolik tahlili"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Xatoliklar tahlili",
#         manual_parameters=[
#             openapi.Parameter('days', openapi.IN_QUERY, description="Qancha kunlik ma'lumot", type=openapi.TYPE_INTEGER),
#         ],
#         responses={200: ErrorAnalysisSerializer}
#     )
#     def get(self, request):
#         days = int(request.GET.get('days', 30))
#         analysis = ErrorAnalysisService.get_error_analysis(request.user, days)
#
#         return Response({
#             'success': True,
#             'data': analysis
#         })
#
#
# class RecommendationListView(generics.ListAPIView):
#     """Tavsiyalar ro'yxati"""
#     serializer_class = RecommendationSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         status_filter = self.request.GET.get('status', 'pending')
#         return RecommendationService.get_user_recommendations(self.request.user, status_filter)
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining tavsiyalari",
#         manual_parameters=[
#             openapi.Parameter('status', openapi.IN_QUERY, description="Status", type=openapi.TYPE_STRING, enum=['pending', 'viewed', 'completed']),
#         ],
#         responses={200: RecommendationSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class MarkRecommendationViewedView(APIView):
#     """Tavsiyani ko'rilgan deb belgilash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Tavsiyani ko'rilgan deb belgilash",
#         manual_parameters=[
#             openapi.Parameter('recommendation_id', openapi.IN_QUERY, description="Recommendation ID", type=openapi.TYPE_INTEGER, required=True)
#         ],
#         responses={200: RecommendationSerializer}
#     )
#     def post(self, request):
#         recommendation_id = request.GET.get('recommendation_id')
#         if not recommendation_id:
#             return Response({
#                 'error': 'Recommendation ID kerak'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             recommendation = RecommendationService.mark_recommendation_viewed(
#                 request.user, recommendation_id
#             )
#
#             return Response({
#                 'message': 'Tavsiya ko\'rilgan deb belgilandi',
#                 'recommendation': RecommendationSerializer(recommendation).data
#             }, status=status.HTTP_200_OK)
#
#         except ValueError as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 'error': 'Tavsiyani belgilashda xatolik',
#                 'detail': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class CompleteRecommendationView(APIView):
#     """Tavsiyani bajarilgan deb belgilash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Tavsiyani bajarilgan deb belgilash",
#         manual_parameters=[
#             openapi.Parameter('recommendation_id', openapi.IN_QUERY, description="Recommendation ID", type=openapi.TYPE_INTEGER, required=True)
#         ],
#         responses={200: RecommendationSerializer}
#     )
#     def post(self, request):
#         recommendation_id = request.GET.get('recommendation_id')
#         if not recommendation_id:
#             return Response({
#                 'error': 'Recommendation ID kerak'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             recommendation = RecommendationService.complete_recommendation(
#                 request.user, recommendation_id
#             )
#
#             return Response({
#                 'message': 'Tavsiya bajarilgan deb belgilandi',
#                 'recommendation': RecommendationSerializer(recommendation).data
#             }, status=status.HTTP_200_OK)
#
#         except ValueError as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 'error': 'Tavsiyani belgilashda xatolik',
#                 'detail': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class DashboardView(APIView):
#     """Dashboard"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchi dashboard statistikasi",
#         responses={200: DashboardStatsSerializer}
#     )
#     def get(self, request):
#         stats = DashboardService.get_dashboard_stats(request.user)
#
#         return Response({
#             'success': True,
#             'data': stats
#         })
#
#
# # Admin views
# class AdminAllSessionsView(generics.ListAPIView):
#     """Barcha test sessiyalari (Admin)"""
#     serializer_class = TestSessionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = TestSession.objects.all().order_by('-created_at')
#
#     @swagger_auto_schema(
#         operation_description="Barcha test sessiyalari ro'yxati (Admin)",
#         responses={200: TestSessionSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class AdminSessionDetailView(generics.RetrieveAPIView):
#     """Test sessiyasi detail (Admin)"""
#     serializer_class = TestSessionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = TestSession.objects.all()
#     lookup_field = 'id'
#
#     @swagger_auto_schema(
#         operation_description="Test sessiyasi detail ma'lumotlari (Admin)",
#         responses={200: TestSessionSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
