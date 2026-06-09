from django.urls import path
from .views import (
    ListeningTestListCreateAPIView, ListeningTestRetrieveUpdateDestroyAPIView,
    ReadingPassageListCreateAPIView, ReadingPassageRetrieveUpdateDestroyAPIView,
    WritingTaskListCreateAPIView, WritingTaskRetrieveUpdateDestroyAPIView,
    SmartArticleListCreateAPIView, SmartArticleRetrieveUpdateDestroyAPIView,
    ListeningMaterialListCreateAPIView, ListeningMaterialRetrieveUpdateDestroyAPIView,
    VocabularyWordListCreateAPIView, VocabularyWordRetrieveUpdateDestroyAPIView,
    import_vocab_word
)
from .views_dashboard import dashboard_statistics, quick_stats
from .views_myreport import my_report_data
from .views_admin_dashboard import admin_dashboard_statistics
from .views_admin_panel import (
    admin_users_list, admin_user_detail, admin_adjust_coins, admin_toggle_subscription,
    admin_payments_list, admin_approve_payment, admin_reject_payment,
    admin_logs, admin_coin_transactions,
)

app_name = 'modules'

urlpatterns = [
    path('listening-tests/', ListeningTestListCreateAPIView.as_view(), name='listening-test-list-create'),
    path('listening-tests/<int:id>/', ListeningTestRetrieveUpdateDestroyAPIView.as_view(), name='listening-test-detail'),
    path('reading-passages/', ReadingPassageListCreateAPIView.as_view(), name='reading-passage-list-create'),
    path('reading-passages/<int:id>/', ReadingPassageRetrieveUpdateDestroyAPIView.as_view(), name='reading-passage-detail'),
    path('writing-tasks/', WritingTaskListCreateAPIView.as_view(), name='writing-task-list-create'),
    path('writing-tasks/<int:id>/', WritingTaskRetrieveUpdateDestroyAPIView.as_view(), name='writing-task-detail'),
    path('smart-articles/', SmartArticleListCreateAPIView.as_view(), name='smart-article-list-create'),
    path('smart-articles/<int:id>/', SmartArticleRetrieveUpdateDestroyAPIView.as_view(), name='smart-article-detail'),
    path('listening-materials/', ListeningMaterialListCreateAPIView.as_view(), name='listening-material-list-create'),
    path('listening-materials/<int:id>/', ListeningMaterialRetrieveUpdateDestroyAPIView.as_view(), name='listening-material-detail'),
    path('vocabulary-words/', VocabularyWordListCreateAPIView.as_view(), name='vocabulary-word-list-create'),
    path('vocabulary-words/<int:id>/', VocabularyWordRetrieveUpdateDestroyAPIView.as_view(), name='vocabulary-word-detail'),
    path('vocabulary/import/<int:pk>/', import_vocab_word, name='import_vocab_word'),
    
    # Dashboard endpoints
    path('dashboard/statistics/', dashboard_statistics, name='dashboard-statistics'),
    path('dashboard/quick-stats/', quick_stats, name='dashboard-quick-stats'),
    
    # MyReport endpoint
    path('my-report/', my_report_data, name='my-report'),
    
    # Admin Dashboard endpoint
    path('admin-dashboard/', admin_dashboard_statistics, name='admin-dashboard-statistics'),
    
    # Admin Panel endpoints (users, payments, logs)
    path('admin-dashboard/users/', admin_users_list, name='admin-users-list'),
    path('admin-dashboard/users/<int:user_id>/', admin_user_detail, name='admin-user-detail'),
    path('admin-dashboard/users/coins/', admin_adjust_coins, name='admin-adjust-coins'),
    path('admin-dashboard/users/subscription/', admin_toggle_subscription, name='admin-toggle-subscription'),
    path('admin-dashboard/payments/', admin_payments_list, name='admin-payments-list'),
    path('admin-dashboard/payments/approve/', admin_approve_payment, name='admin-approve-payment'),
    path('admin-dashboard/payments/reject/', admin_reject_payment, name='admin-reject-payment'),
    path('admin-dashboard/logs/', admin_logs, name='admin-logs'),
    path('admin-dashboard/coin-transactions/', admin_coin_transactions, name='admin-coin-transactions'),
]
