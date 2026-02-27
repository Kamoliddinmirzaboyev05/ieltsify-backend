from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from accounts.permissions import IsRegularUser, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from .models import SubscriptionPlan, CoinPack, Payment
from .serializers import (
    SubscriptionPlanReadSerializer,
    SubscriptionPlanWriteSerializer,
    UserSubscriptionSerializer,
    CoinWalletSerializer,
    CoinTransactionSerializer,
    CoinPackReadSerializer,
    CoinPackWriteSerializer,
    CreateSubscriptionPaymentSerializer,
    CreateCoinPackPaymentSerializer,
    PaymentSerializer,
    PaymentCallbackSerializer,
)
from .services import (
    SubscriptionService,
    WalletService,
    PaymentService,
)
from .payment_services import PaymentGatewayService
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class SubscriptionPlanListCreateView(generics.ListCreateAPIView):
    queryset = SubscriptionPlan.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsRegularUser() | IsAdminUser()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.role != "admin":
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SubscriptionPlanReadSerializer
        return SubscriptionPlanWriteSerializer


class SubscriptionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan.objects.all()
    lookup_field = "id"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SubscriptionPlanReadSerializer
        return SubscriptionPlanWriteSerializer


class CoinPackListCreateView(generics.ListCreateAPIView):
    queryset = CoinPack.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated or user.role != "admin":
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CoinPackReadSerializer
        return CoinPackWriteSerializer


class CoinPackDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoinPack.objects.all()
    lookup_field = "id"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated or user.role != "admin":
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CoinPackReadSerializer
        return CoinPackWriteSerializer


class CurrentSubscriptionView(generics.RetrieveAPIView):
    """
    Foydalanuvchining joriy aktiv obunasi.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def get_object(self):
        sub = SubscriptionService.get_active_subscription(self.request.user)
        if not sub:
            raise NotFound("Aktiv obuna topilmadi")
        return sub

    @swagger_auto_schema(
        operation_description="Joriy aktiv obunani olish",
        responses={200: UserSubscriptionSerializer},
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class WalletDetailView(generics.RetrieveAPIView):
    """
    Foydalanuvchi coin balansi.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CoinWalletSerializer

    def get_object(self):
        return WalletService.get_or_create_wallet(self.request.user)

    @swagger_auto_schema(
        operation_description="Foydalanuvchi coin balansi",
        responses={200: CoinWalletSerializer},
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class CoinTransactionListView(generics.ListAPIView):
    """
    Coin tranzaksiyalar tarixi.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CoinTransactionSerializer

    def get_queryset(self):
        return self.request.user.coin_transactions.all().order_by(
            "-created_at"
        )[:100]

    @swagger_auto_schema(
        operation_description="Foydalanuvchi coin tranzaksiyalari ro'yxati",
        responses={200: CoinTransactionSerializer(many=True)},
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class CreateSubscriptionPaymentView(generics.CreateAPIView):
    """
    Subscription plan uchun payment yaratish.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateSubscriptionPaymentSerializer

    @swagger_auto_schema(
        operation_description="Subscription plan uchun to'lov yaratish (Click/Payme)",
        request_body=CreateSubscriptionPaymentSerializer,
        responses={201: PaymentSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_id = serializer.validated_data["plan_id"]
        provider = serializer.validated_data["provider"]

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise NotFound("Bunday plan topilmadi")

        payment = PaymentService.create_subscription_payment(
            user=request.user,
            plan=plan,
            provider=provider,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class CreateCoinPackPaymentView(generics.CreateAPIView):
    """
    Coin pack uchun payment yaratish.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateCoinPackPaymentSerializer

    @swagger_auto_schema(
        operation_description="Coin pack uchun to'lov yaratish (Click/Payme)",
        request_body=CreateCoinPackPaymentSerializer,
        responses={201: PaymentSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pack_id = serializer.validated_data["coin_pack_id"]
        provider = serializer.validated_data["provider"]

        try:
            pack = CoinPack.objects.get(id=pack_id, is_active=True)
        except CoinPack.DoesNotExist:
            raise NotFound("Bunday coin pack topilmadi")

        payment = PaymentService.create_coin_pack_payment(
            user=request.user,
            coin_pack=pack,
            provider=provider,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentCallbackView(generics.CreateAPIView):
    """
    Click/Payme callback endpointi.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = PaymentCallbackSerializer

    @swagger_auto_schema(
        operation_description="Click/Payme callback endpointi",
        request_body=PaymentCallbackSerializer,
        responses={200: PaymentSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_id = serializer.validated_data.get("payment_id")
        status_value = serializer.validated_data["status"]
        provider_payment_id = serializer.validated_data.get(
            "provider_payment_id"
        )

        if not payment_id:
            raise ValidationError("payment_id ko'rsatilmagan")

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            raise NotFound("Payment topilmadi")

        # Security tekshiruv - callback ni tasdiqlash
        if payment.provider == Payment.PROVIDER_CLICK:
            if not PaymentGatewayService.verify_click_callback(request.data):
                return Response(
                    {"error": "Invalid Click callback signature"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif payment.provider == Payment.PROVIDER_PAYME:
            if not PaymentGatewayService.verify_payme_callback(request.data):
                return Response(
                    {"error": "Invalid Payme callback signature"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        payment = PaymentService.handle_payment_callback(
            payment=payment,
            status=status_value,
            provider_payment_id=provider_payment_id,
            extra_data=request.data,
        )

        return Response(PaymentSerializer(payment).data)
