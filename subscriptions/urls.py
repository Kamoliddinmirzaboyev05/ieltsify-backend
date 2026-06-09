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
    SubmitPaymentWithReceiptView,
    MyPaymentsView,
    UsageLimitsView,
    CoinServiceCostsView,
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
    path(
        "subs/submit-payment/",
        SubmitPaymentWithReceiptView.as_view(),
        name="submit-payment-receipt",
    ),
    path(
        "subs/my-payments/",
        MyPaymentsView.as_view(),
        name="my-payments",
    ),
    path(
        "subs/usage-limits/",
        UsageLimitsView.as_view(),
        name="usage-limits",
    ),
    path(
        "subs/coin-service-costs/",
        CoinServiceCostsView.as_view(),
        name="coin-service-costs",
    ),
]


