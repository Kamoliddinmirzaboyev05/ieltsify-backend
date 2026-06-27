from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
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
            return [permissions.IsAuthenticated()]
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
            if not PaymentGatewayService.verify_click_callback(request.data, payment):
                return Response(
                    {"error": "Invalid Click callback signature"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif payment.provider == Payment.PROVIDER_PAYME:
            if not PaymentGatewayService.verify_payme_callback(request.data, payment):
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


class SubmitPaymentWithReceiptView(generics.CreateAPIView):
    """
    Foydalanuvchi to'lov cheki bilan to'lov so'rovi yuboradi.
    Receipt image + plan_id yoki coin_pack_id yuboriladi.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')
        coin_pack_id = request.data.get('coin_pack_id')
        receipt_image = request.FILES.get('receipt_image')

        if not receipt_image:
            return Response(
                {'error': 'To\'lov cheki (receipt_image) yuklash majburiy'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not plan_id and not coin_pack_id:
            return Response(
                {'error': 'plan_id yoki coin_pack_id yuborish kerak'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment_data = {
                'user': request.user,
                'provider': 'click',
                'status': Payment.STATUS_PENDING,
                'receipt_image': receipt_image,
            }

            if plan_id:
                plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
                payment_data['plan'] = plan
                payment_data['amount_uzs'] = plan.price_uzs
            elif coin_pack_id:
                pack = CoinPack.objects.get(id=coin_pack_id, is_active=True)
                payment_data['coin_pack'] = pack
                payment_data['amount_uzs'] = pack.price_uzs

            payment = Payment.objects.create(**payment_data)

            return Response({
                'success': True,
                'message': 'To\'lov so\'rovi yuborildi. Admin tasdiqlashini kuting.',
                'payment_id': payment.id,
                'status': payment.status,
                'amount': payment.amount_uzs,
            }, status=status.HTTP_201_CREATED)

        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        except CoinPack.DoesNotExist:
            return Response({'error': 'Coin pack topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyPaymentsView(generics.ListAPIView):
    """
    Foydalanuvchining o'z to'lovlari ro'yxati.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:20]

        results = []
        for p in payments:
            results.append({
                'id': p.id,
                'amount_uzs': p.amount_uzs,
                'status': p.status,
                'provider': p.provider,
                'plan_name': p.plan.name if p.plan else None,
                'coin_pack_name': p.coin_pack.name if p.coin_pack else None,
                'receipt_image_url': p.receipt_image.url if p.receipt_image else None,
                'created_at': p.created_at.isoformat(),
            })

        return Response({
            'success': True,
            'data': results,
        })


class UsageLimitsView(generics.RetrieveAPIView):
    """
    Foydalanuvchining joriy tarif limitlari va foydalanish holati.
    Dashboard uchun asosiy endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .entitlement_service import EntitlementService
        summary = EntitlementService.get_usage_limits_summary(request.user)
        return Response({'success': True, 'data': summary})


class CoinServiceCostsView(generics.ListAPIView):
    """
    AI xizmatlarining coin narxlari ro'yxati.
    Frontend uchun — coin modal'da ko'rsatish.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .models import CoinServiceCost
        costs = CoinServiceCost.objects.filter(is_active=True)
        data = [
            {
                'service_code': c.service_code,
                'name': c.name,
                'cost_coins': c.cost_coins,
            }
            for c in costs
        ]
        return Response({'success': True, 'data': data})
