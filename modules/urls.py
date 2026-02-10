# from django.urls import path
# from .views import (
#     TestCategoryListView, TestListView, TestDetailView,
#     StartTestView, SubmitAnswerView, CompleteTestView,
#     UserTestAttemptsView, TestAttemptDetailView, TestStatsView,
#     LeaderboardView, RecommendationsView, StudyMaterialListView,
#     StudyMaterialDetailView, AccessMaterialView, ProgressAnalyticsView,
#     TestReviewView, AdminTestCategoryListCreateView,
#     AdminTestDetailView, AdminAllAttemptsView
# )
#
# app_name = 'modules'
#
# urlpatterns = [
#     # Public endpoints
#     path('categories/', TestCategoryListView.as_view(), name='category-list'),
#     path('tests/', TestListView.as_view(), name='test-list'),
#     path('tests/<int:id>/', TestDetailView.as_view(), name='test-detail'),
#     path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
#
#     # Study materials
#     path('materials/', StudyMaterialListView.as_view(), name='material-list'),
#     path('materials/<int:id>/', StudyMaterialDetailView.as_view(), name='material-detail'),
#
#     # Authenticated endpoints
#     path('tests/start/', StartTestView.as_view(), name='start-test'),
#     path('tests/submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
#     path('tests/complete/', CompleteTestView.as_view(), name='complete-test'),
#     path('tests/my-attempts/', UserTestAttemptsView.as_view(), name='my-attempts'),
#     path('tests/attempts/<int:id>/', TestAttemptDetailView.as_view(), name='attempt-detail'),
#     path('tests/stats/', TestStatsView.as_view(), name='test-stats'),
#     path('tests/recommendations/', RecommendationsView.as_view(), name='recommendations'),
#     path('tests/attempts/<int:id>/review/', TestReviewView.as_view(), name='test-review'),
#     path('materials/access/', AccessMaterialView.as_view(), name='access-material'),
#     path('analytics/progress/', ProgressAnalyticsView.as_view(), name='progress-analytics'),
#
#     # Admin endpoints
#     path('admin/categories/', AdminTestCategoryListCreateView.as_view(), name='admin-categories'),
#     path('admin/tests/<int:id>/', AdminTestDetailView.as_view(), name='admin-test-detail'),
#     path('admin/attempts/', AdminAllAttemptsView.as_view(), name='admin-attempts'),
# ]
