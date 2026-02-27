from django.urls import path

from .views import (
    SubscriptionPlanListCreateView,
    SubscriptionPlanDetailView,
    CurrentSubscriptionView,
    WalletDetailView,
    CoinTransactionListView,
    CoinPackListCreateView,
    CoinPackDetailView,
    CreateSubscriptionPaymentView,
    CreateCoinPackPaymentView,
    PaymentCallbackView,
)

app_name = "subscriptions"

urlpatterns = [
    path(
        "subscription-plans/",
        SubscriptionPlanListCreateView.as_view(),
        name="subscription-plan-list-create",
    ),
    path(
        "subscription-plans/<int:id>/",
        SubscriptionPlanDetailView.as_view(),
        name="subscription-plan-detail",
    ),
    path("coin-packs/", CoinPackListCreateView.as_view(), name="coinpack-list-create"),
    path("coin-packs/<int:id>/", CoinPackDetailView.as_view(), name="coinpack-detail"),
    path("subs/current/", CurrentSubscriptionView.as_view(), name="current-subscription"),
    path("subs/wallet/", WalletDetailView.as_view(), name="wallet-detail"),
    path(
        "subs/transactions/",
        CoinTransactionListView.as_view(),
        name="transaction-list",
    ),
    path(
        "subs/create-subscription-payment/",
        CreateSubscriptionPaymentView.as_view(),
        name="create-subscription-payment",
    ),
    path(
        "subs/create-coin-pack-payment/",
        CreateCoinPackPaymentView.as_view(),
        name="create-coin-pack-payment",
    ),
    path(
        "subs/payments/callback/",
        PaymentCallbackView.as_view(),
        name="payment-callback",
    ),
]


