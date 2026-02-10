# from django.urls import path
# from .views import (
#     SubscriptionPlanListView, SubscriptionPlanDetailView,
#     UserSubscriptionListView, UserSubscriptionDetailView,
#     CreateSubscriptionView, RenewSubscriptionView,
#     CancelSubscriptionView, UpgradeSubscriptionView,
#     SubscriptionUsageView, CheckSubscriptionLimitsView,
#     PaymentHistoryView, PlanComparisonView,
#     AdminSubscriptionStatsView, AdminAllSubscriptionsView,
#     AdminSubscriptionDetailView, AdminAllTransactionsView,
#     reset_daily_usage, check_expired_subscriptions
# )
#
# app_name = 'subscriptions'
#
# urlpatterns = [
#     # Public endpoints
#     path('plans/', SubscriptionPlanListView.as_view(), name='plan-list'),
#     path('plans/<int:id>/', SubscriptionPlanDetailView.as_view(), name='plan-detail'),
#     path('compare/', PlanComparisonView.as_view(), name='plan-comparison'),
#
#     # User subscription endpoints
#     path('my/', UserSubscriptionListView.as_view(), name='my-subscriptions'),
#     path('my/current/', UserSubscriptionDetailView.as_view(), name='my-current-subscription'),
#     path('create/', CreateSubscriptionView.as_view(), name='create-subscription'),
#     path('renew/', RenewSubscriptionView.as_view(), name='renew-subscription'),
#     path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
#     path('upgrade/', UpgradeSubscriptionView.as_view(), name='upgrade-subscription'),
#     path('usage/', SubscriptionUsageView.as_view(), name='subscription-usage'),
#     path('check-limits/', CheckSubscriptionLimitsView.as_view(), name='check-limits'),
#     path('payment-history/', PaymentHistoryView.as_view(), name='payment-history'),
#
#     # Admin endpoints
#     path('admin/stats/', AdminSubscriptionStatsView.as_view(), name='admin-stats'),
#     path('admin/all/', AdminAllSubscriptionsView.as_view(), name='admin-all-subscriptions'),
#     path('admin/<int:id>/', AdminSubscriptionDetailView.as_view(), name='admin-subscription-detail'),
#     path('admin/transactions/', AdminAllTransactionsView.as_view(), name='admin-transactions'),
#     path('admin/reset-daily-usage/', reset_daily_usage, name='admin-reset-daily-usage'),
#     path('admin/check-expired/', check_expired_subscriptions, name='admin-check-expired'),
# ]
