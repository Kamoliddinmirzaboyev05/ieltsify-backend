# from django.urls import path
# from .views import (
#     TestSessionListView, StartTestSessionView, StartSectionView,
#     SubmitResponseView, CompleteSectionView, CompleteSessionView,
#     SessionAnalyticsView, ProgressTrackerListView, SetGoalView,
#     UpdateProgressView, StudySessionListView, StartStudySessionView,
#     UpdateStudySessionView, StudyAnalyticsView, ErrorLogListView,
#     ErrorAnalysisView, RecommendationListView, MarkRecommendationViewedView,
#     CompleteRecommendationView, DashboardView, AdminAllSessionsView,
#     AdminSessionDetailView
# )
#
# app_name = 'attempts'
#
# urlpatterns = [
#     # Test sessions
#     path('sessions/', TestSessionListView.as_view(), name='session-list'),
#     path('sessions/start/', StartTestSessionView.as_view(), name='start-session'),
#     path('sessions/start-section/', StartSectionView.as_view(), name='start-section'),
#     path('sessions/submit-response/', SubmitResponseView.as_view(), name='submit-response'),
#     path('sessions/complete-section/', CompleteSectionView.as_view(), name='complete-section'),
#     path('sessions/complete/', CompleteSessionView.as_view(), name='complete-session'),
#     path('sessions/analytics/', SessionAnalyticsView.as_view(), name='session-analytics'),
#
#     # Progress tracking
#     path('progress/', ProgressTrackerListView.as_view(), name='progress-list'),
#     path('progress/set-goal/', SetGoalView.as_view(), name='set-goal'),
#     path('progress/update/', UpdateProgressView.as_view(), name='update-progress'),
#
#     # Study sessions
#     path('study/', StudySessionListView.as_view(), name='study-list'),
#     path('study/start/', StartStudySessionView.as_view(), name='start-study'),
#     path('study/update/', UpdateStudySessionView.as_view(), name='update-study'),
#     path('study/analytics/', StudyAnalyticsView.as_view(), name='study-analytics'),
#
#     # Error tracking
#     path('errors/', ErrorLogListView.as_view(), name='error-list'),
#     path('errors/analysis/', ErrorAnalysisView.as_view(), name='error-analysis'),
#
#     # Recommendations
#     path('recommendations/', RecommendationListView.as_view(), name='recommendation-list'),
#     path('recommendations/view/', MarkRecommendationViewedView.as_view(), name='mark-viewed'),
#     path('recommendations/complete/', CompleteRecommendationView.as_view(), name='complete-recommendation'),
#
#     # Dashboard
#     path('dashboard/', DashboardView.as_view(), name='dashboard'),
#
#     # Admin endpoints
#     path('admin/sessions/', AdminAllSessionsView.as_view(), name='admin-sessions'),
#     path('admin/sessions/<int:id>/', AdminSessionDetailView.as_view(), name='admin-session-detail'),
# ]
