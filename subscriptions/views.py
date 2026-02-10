# from rest_framework import status, permissions, generics, mixins
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# from django.utils.decorators import method_decorator
# from django.db.models import Count, Sum, Q
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from .serializers import (
#     SubscriptionPlanSerializer, UserSubscriptionSerializer,
#     CreateSubscriptionSerializer, RenewSubscriptionSerializer,
#     CancelSubscriptionSerializer, UpgradeSubscriptionSerializer,
#     SubscriptionStatsSerializer, PlanComparisonSerializer,
#     SubscriptionUsageSerializer, PaymentHistorySerializer,
#     SubscriptionTransactionSerializer
# )
# from .services import SubscriptionService, SubscriptionNotificationService
# from accounts.permissions import IsAdminUser, IsOwnerOrAdmin
# from .models import SubscriptionPlan, UserSubscription, SubscriptionTransaction
#
#
# class SubscriptionPlanListView(generics.ListAPIView):
#     """Subscription planlar ro'yxati"""
#     queryset = SubscriptionService.get_available_plans()
#     serializer_class = SubscriptionPlanSerializer
#     permission_classes = [permissions.AllowAny]
#
#     @swagger_auto_schema(
#         operation_description="Mavjud subscription planlar ro'yxati",
#         responses={200: SubscriptionPlanSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class SubscriptionPlanDetailView(generics.RetrieveAPIView):
#     """Subscription plan detaili"""
#     queryset = SubscriptionService.get_available_plans()
#     serializer_class = SubscriptionPlanSerializer
#     permission_classes = [permissions.AllowAny]
#     lookup_field = 'id'
#
#     @swagger_auto_schema(
#         operation_description="Subscription plan detail ma'lumotlari",
#         responses={200: SubscriptionPlanSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class UserSubscriptionListView(generics.ListAPIView):
#     """Foydalanuvchi subscriptionlari"""
#     serializer_class = UserSubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return UserSubscription.objects.filter(user=self.request.user).order_by('-created_at')
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining subscriptionlari ro'yxati",
#         responses={200: UserSubscriptionSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class UserSubscriptionDetailView(generics.RetrieveAPIView):
#     """Foydalanuvchi subscription detaili"""
#     serializer_class = UserSubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_object(self):
#         return SubscriptionService.get_user_subscription(self.request.user)
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining joriy subscriptioni",
#         responses={200: UserSubscriptionSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         subscription = self.get_object()
#         if not subscription:
#             return Response({
#                 'error': 'Subscription topilmadi'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = self.get_serializer(subscription)
#         return Response(serializer.data)
#
#
# class CreateSubscriptionView(APIView):
#     """Yangi subscription yaratish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Yangi subscription yaratish",
#         request_body=CreateSubscriptionSerializer,
#         responses={201: UserSubscriptionSerializer}
#     )
#     def post(self, request):
#         serializer = CreateSubscriptionSerializer(
#             data=request.data,
#             context={'request': request}
#         )
#
#         if serializer.is_valid():
#             try:
#                 plan_id = serializer.validated_data['plan_id']
#                 payment_method = serializer.validated_data['payment_method']
#                 auto_renew = serializer.validated_data.get('auto_renew', False)
#
#                 # To'lovni qayta ishlash
#                 plan = SubscriptionService.get_plan_by_id(plan_id)
#                 payment_success, payment_message = SubscriptionService.process_payment(
#                     request.user, plan, payment_method
#                 )
#
#                 if not payment_success:
#                     return Response({
#                         'error': 'To\'lov amalga oshmadi',
#                         'detail': payment_message
#                     }, status=status.HTTP_400_BAD_REQUEST)
#
#                 # Subscription yaratish
#                 subscription, transaction = SubscriptionService.create_subscription(
#                     request.user, plan_id, payment_method, auto_renew
#                 )
#
#                 # Notification yuborish
#                 SubscriptionNotificationService.send_welcome_email(subscription)
#
#                 return Response({
#                     'message': 'Subscription muvaffaqiyatli yaratildi',
#                     'subscription': UserSubscriptionSerializer(subscription).data,
#                     'transaction': SubscriptionTransactionSerializer(transaction).data
#                 }, status=status.HTTP_201_CREATED)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Subscription yaratishda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class RenewSubscriptionView(APIView):
#     """Subscriptionni yangilash"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Subscriptionni yangilash",
#         request_body=RenewSubscriptionSerializer,
#         responses={200: UserSubscriptionSerializer}
#     )
#     def post(self, request):
#         serializer = RenewSubscriptionSerializer(
#             data=request.data,
#             context={'request': request}
#         )
#
#         if serializer.is_valid():
#             try:
#                 payment_method = serializer.validated_data['payment_method']
#
#                 # To'lovni qayta ishlash
#                 current_subscription = SubscriptionService.get_active_subscription(request.user)
#                 payment_success, payment_message = SubscriptionService.process_payment(
#                     request.user, current_subscription.plan, payment_method, 'renewal'
#                 )
#
#                 if not payment_success:
#                     return Response({
#                         'error': 'To\'lov amalga oshmadi',
#                         'detail': payment_message
#                     }, status=status.HTTP_400_BAD_REQUEST)
#
#                 # Subscriptionni yangilash
#                 subscription, transaction = SubscriptionService.renew_subscription(
#                     request.user, payment_method
#                 )
#
#                 return Response({
#                     'message': 'Subscription muvaffaqiyatli yangilandi',
#                     'subscription': UserSubscriptionSerializer(subscription).data,
#                     'transaction': SubscriptionTransactionSerializer(transaction).data
#                 }, status=status.HTTP_200_OK)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Subscriptionni yangilashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class CancelSubscriptionView(APIView):
#     """Subscriptionni bekor qilish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Subscriptionni bekor qilish",
#         request_body=CancelSubscriptionSerializer,
#         responses={200: openapi.Response(description="Subscription bekor qilindi")}
#     )
#     def post(self, request):
#         serializer = CancelSubscriptionSerializer(
#             data=request.data,
#             context={'request': request}
#         )
#
#         if serializer.is_valid():
#             try:
#                 reason = serializer.validated_data.get('reason')
#                 immediate = serializer.validated_data.get('immediate', False)
#
#                 subscription, transaction = SubscriptionService.cancel_subscription(
#                     request.user, reason, immediate
#                 )
#
#                 # Notification yuborish
#                 SubscriptionNotificationService.send_cancellation_email(subscription, reason)
#
#                 return Response({
#                     'message': 'Subscription bekor qilindi',
#                     'subscription': UserSubscriptionSerializer(subscription).data,
#                     'immediate': immediate
#                 }, status=status.HTTP_200_OK)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Subscriptionni bekor qilishda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UpgradeSubscriptionView(APIView):
#     """Subscriptionni yangilash (upgrade)"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Subscriptionni yangilash (upgrade)",
#         request_body=UpgradeSubscriptionSerializer,
#         responses={200: UserSubscriptionSerializer}
#     )
#     def post(self, request):
#         serializer = UpgradeSubscriptionSerializer(
#             data=request.data,
#             context={'request': request}
#         )
#
#         if serializer.is_valid():
#             try:
#                 new_plan_id = serializer.validated_data['new_plan_id']
#                 payment_method = serializer.validated_data['payment_method']
#
#                 # To'lovni qayta ishlash
#                 new_plan = SubscriptionService.get_plan_by_id(new_plan_id)
#                 current_subscription = SubscriptionService.get_active_subscription(request.user)
#                 price_difference = new_plan.price - current_subscription.plan.price
#
#                 # Agar price difference bo'lsa, to'lov qilish
#                 if price_difference > 0:
#                     payment_success, payment_message = SubscriptionService.process_payment(
#                         request.user, new_plan, payment_method, 'upgrade'
#                     )
#
#                     if not payment_success:
#                         return Response({
#                             'error': 'To\'lov amalga oshmadi',
#                             'detail': payment_message
#                         }, status=status.HTTP_400_BAD_REQUEST)
#
#                 # Subscriptionni yangilash
#                 subscription, transaction = SubscriptionService.upgrade_subscription(
#                     request.user, new_plan_id, payment_method
#                 )
#
#                 return Response({
#                     'message': 'Subscription muvaffaqiyatli yangilandi',
#                     'subscription': UserSubscriptionSerializer(subscription).data,
#                     'transaction': SubscriptionTransactionSerializer(transaction).data
#                 }, status=status.HTTP_200_OK)
#
#             except ValueError as e:
#                 return Response({
#                     'error': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({
#                     'error': 'Subscriptionni yangilashda xatolik',
#                     'detail': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class SubscriptionUsageView(APIView):
#     """Subscription usage ma'lumotlari"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Subscription usage ma'lumotlari",
#         responses={200: SubscriptionUsageSerializer}
#     )
#     def get(self, request):
#         subscription = SubscriptionService.get_active_subscription(request.user)
#
#         if not subscription:
#             return Response({
#                 'error': 'Active subscription topilmadi'
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = SubscriptionUsageSerializer(subscription)
#         return Response({
#             'success': True,
#             'data': serializer.data
#         })
#
#
# class CheckSubscriptionLimitsView(APIView):
#     """Subscription limitlarini tekshirish"""
#     permission_classes = [permissions.IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Subscription limitlarini tekshirish",
#         manual_parameters=[
#             openapi.Parameter(
#                 'type',
#                 openapi.IN_QUERY,
#                 description="Test turi (test/study_material)",
#                 type=openapi.TYPE_STRING,
#                 enum=['test', 'study_material']
#             )
#         ],
#         responses={200: openapi.Response(description="Limit tekshiruv natijalari")}
#     )
#     def get(self, request):
#         test_type = request.GET.get('type', 'test')
#
#         can_access, message = SubscriptionService.check_subscription_limits(
#             request.user, test_type
#         )
#
#         return Response({
#             'success': True,
#             'can_access': can_access,
#             'message': message,
#             'type': test_type
#         })
#
#
# class PaymentHistoryView(generics.ListAPIView):
#     """To'lov tarixi"""
#     serializer_class = PaymentHistorySerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return SubscriptionService.get_payment_history(self.request.user)
#
#     @swagger_auto_schema(
#         operation_description="Foydalanuvchining to'lov tarixi",
#         responses={200: PaymentHistorySerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class PlanComparisonView(APIView):
#     """Planlarni solishtirish"""
#     permission_classes = [permissions.AllowAny]
#
#     @swagger_auto_schema(
#         operation_description="Subscription planlarini solishtirish",
#         responses={200: PlanComparisonSerializer}
#     )
#     def get(self, request):
#         plans = SubscriptionService.get_available_plans()
#         user_subscription = None
#
#         if request.user.is_authenticated:
#             user_subscription = SubscriptionService.get_user_subscription(request.user)
#
#         data = {
#             'plans': SubscriptionPlanSerializer(plans, many=True).data
#         }
#
#         if user_subscription:
#             data['user_current_plan'] = UserSubscriptionSerializer(user_subscription).data
#
#         return Response({
#             'success': True,
#             'data': data
#         })
#
#
# # Admin views
# class AdminSubscriptionStatsView(APIView):
#     """Admin uchun subscription statistikasi"""
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#
#     @swagger_auto_schema(
#         operation_description="Subscription statistikasi (Admin)",
#         responses={200: SubscriptionStatsSerializer}
#     )
#     def get(self, request):
#         stats = SubscriptionService.get_subscription_stats()
#
#         return Response({
#             'success': True,
#             'data': stats
#         })
#
#
# class AdminAllSubscriptionsView(generics.ListAPIView):
#     """Barcha subscriptionlar (Admin)"""
#     serializer_class = UserSubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = UserSubscription.objects.all().order_by('-created_at')
#
#     @swagger_auto_schema(
#         operation_description="Barcha subscriptionlar ro'yxati (Admin)",
#         responses={200: UserSubscriptionSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# class AdminSubscriptionDetailView(generics.RetrieveUpdateAPIView):
#     """Subscription detail (Admin)"""
#     serializer_class = UserSubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = UserSubscription.objects.all()
#     lookup_field = 'id'
#
#     @swagger_auto_schema(
#         operation_description="Subscription detail ma'lumotlari (Admin)",
#         responses={200: UserSubscriptionSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#     @swagger_auto_schema(
#         operation_description="Subscriptionni yangilash (Admin)",
#         request_body=UserSubscriptionSerializer,
#         responses={200: UserSubscriptionSerializer}
#     )
#     def patch(self, request, *args, **kwargs):
#         return super().partial_update(request, *args, **kwargs)
#
#
# class AdminAllTransactionsView(generics.ListAPIView):
#     """Barcha tranzaksiyalar (Admin)"""
#     serializer_class = SubscriptionTransactionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     queryset = SubscriptionTransaction.objects.all().order_by('-created_at')
#
#     @swagger_auto_schema(
#         operation_description="Barcha tranzaksiyalar ro'yxati (Admin)",
#         responses={200: SubscriptionTransactionSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
#
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated, IsAdminUser])
# @swagger_auto_schema(
#     operation_description="Kunlik usage larni qayta tiklash (Admin)",
#     responses={200: openapi.Response(description="Daily usage reset completed")}
# )
# def reset_daily_usage(request):
#     """Kunlik usage larni qayta tiklash"""
#     try:
#         SubscriptionService.reset_daily_usage()
#         return Response({
#             'message': 'Daily usage muvaffaqiyatli qayta tiklandi'
#         }, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({
#             'error': 'Daily usage resetda xatolik',
#             'detail': str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated, IsAdminUser])
# @swagger_auto_schema(
#     operation_description="Muddati tugagan subscriptionlarni tekshirish (Admin)",
#     responses={200: openapi.Response(description="Expired subscriptions checked")}
# )
# def check_expired_subscriptions(request):
#     """Muddati tugagan subscriptionlarni tekshirish"""
#     try:
#         count = SubscriptionService.check_expired_subscriptions()
#         return Response({
#             'message': f'{count} ta expired subscription qayta ishlandi'
#         }, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({
#             'error': 'Expired subscriptions checkda xatolik',
#             'detail': str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
