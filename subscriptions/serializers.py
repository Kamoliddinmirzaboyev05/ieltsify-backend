# from rest_framework import serializers
# from django.utils import timezone
# from .models import SubscriptionPlan, UserSubscription, SubscriptionTransaction
#
#
# class SubscriptionPlanSerializer(serializers.ModelSerializer):
#     features_list = serializers.ListField(source='get_features_list', read_only=True)
#     is_popular = serializers.BooleanField(read_only=True)
#
#     class Meta:
#         model = SubscriptionPlan
#         fields = ('id', 'name', 'description', 'price', 'duration_days',
#                  'features', 'features_list', 'is_active', 'is_popular',
#                  'max_tests_per_day', 'max_study_materials', 'priority',
#                  'created_at', 'updated_at')
#         read_only_fields = ('created_at', 'updated_at')
#
#
# class UserSubscriptionSerializer(serializers.ModelSerializer):
#     plan_info = serializers.SerializerMethodField()
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     days_remaining = serializers.SerializerMethodField()
#     usage_percentage = serializers.SerializerMethodField()
#     is_expired = serializers.SerializerMethodField()
#
#     class Meta:
#         model = UserSubscription
#         fields = ('id', 'user_email', 'plan_info', 'status', 'status_display',
#                  'started_at', 'expires_at', 'auto_renew', 'tests_used_today',
#                  'study_materials_used', 'days_remaining', 'usage_percentage',
#                  'is_expired', 'created_at', 'updated_at')
#         read_only_fields = ('user', 'started_at', 'created_at', 'updated_at')
#
#     def get_plan_info(self, obj):
#         if obj.plan:
#             return {
#                 'id': obj.plan.id,
#                 'name': obj.plan.name,
#                 'description': obj.plan.description,
#                 'price': obj.plan.price,
#                 'duration_days': obj.plan.duration_days,
#                 'features': obj.plan.features,
#                 'max_tests_per_day': obj.plan.max_tests_per_day,
#                 'max_study_materials': obj.plan.max_study_materials
#             }
#         return None
#
#     def get_days_remaining(self, obj):
#         if obj.expires_at:
#             remaining = (obj.expires_at - timezone.now()).days
#             return max(0, remaining)
#         return 0
#
#     def get_usage_percentage(self, obj):
#         if obj.plan and obj.plan.max_tests_per_day > 0:
#             return (obj.tests_used_today / obj.plan.max_tests_per_day) * 100
#         return 0
#
#     def get_is_expired(self, obj):
#         return obj.is_expired()
#
#
# class SubscriptionTransactionSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     plan_name = serializers.CharField(source='plan.name', read_only=True)
#     transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
#     payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#
#     class Meta:
#         model = SubscriptionTransaction
#         fields = ('id', 'user_email', 'plan_name', 'transaction_type', 'transaction_type_display',
#                  'amount', 'payment_method', 'payment_method_display', 'status', 'status_display',
#                  'transaction_id', 'gateway_response', 'created_at', 'updated_at')
#         read_only_fields = ('user', 'transaction_id', 'gateway_response', 'created_at', 'updated_at')
#
#
# class CreateSubscriptionSerializer(serializers.Serializer):
#     plan_id = serializers.IntegerField(required=True)
#     payment_method = serializers.ChoiceField(choices=SubscriptionTransaction.PAYMENT_METHOD_CHOICES)
#     auto_renew = serializers.BooleanField(default=False)
#
#     def validate_plan_id(self, value):
#         try:
#             plan = SubscriptionPlan.objects.get(id=value, is_active=True)
#             return value
#         except SubscriptionPlan.DoesNotExist:
#             raise serializers.ValidationError("Noto'g'ri yoki nofaol subscription plani")
#
#     def validate(self, attrs):
#         user = self.context['request'].user
#
#         # Active subscription borligini tekshirish
#         active_subscription = UserSubscription.objects.filter(
#             user=user,
#             status='active'
#         ).first()
#
#         if active_subscription:
#             raise serializers.ValidationError("Sizda allaqachon active subscription mavjud")
#
#         return attrs
#
#
# class RenewSubscriptionSerializer(serializers.Serializer):
#     payment_method = serializers.ChoiceField(choices=SubscriptionTransaction.PAYMENT_METHOD_CHOICES)
#
#     def validate(self, attrs):
#         user = self.context['request'].user
#
#         # Active subscription yo'qligini tekshirish
#         active_subscription = UserSubscription.objects.filter(
#             user=user,
#             status='active'
#         ).first()
#
#         if not active_subscription:
#             raise serializers.ValidationError("Active subscription topilmadi")
#
#         return attrs
#
#
# class CancelSubscriptionSerializer(serializers.Serializer):
#     reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
#     immediate = serializers.BooleanField(default=False)
#
#     def validate(self, attrs):
#         user = self.context['request'].user
#
#         # Active subscription borligini tekshirish
#         active_subscription = UserSubscription.objects.filter(
#             user=user,
#             status='active'
#         ).first()
#
#         if not active_subscription:
#             raise serializers.ValidationError("Active subscription topilmadi")
#
#         return attrs
#
#
# class SubscriptionStatsSerializer(serializers.Serializer):
#     total_subscriptions = serializers.IntegerField()
#     active_subscriptions = serializers.IntegerField()
#     expired_subscriptions = serializers.IntegerField()
#     cancelled_subscriptions = serializers.IntegerField()
#     total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
#     current_month_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
#     most_popular_plan = serializers.DictField()
#     subscription_trends = serializers.ListField()
#
#
# class PlanComparisonSerializer(serializers.Serializer):
#     plans = SubscriptionPlanSerializer(many=True)
#     user_current_plan = UserSubscriptionSerializer(required=False)
#
#
# class UpgradeSubscriptionSerializer(serializers.Serializer):
#     new_plan_id = serializers.IntegerField(required=True)
#     payment_method = serializers.ChoiceField(choices=SubscriptionTransaction.PAYMENT_METHOD_CHOICES)
#
#     def validate_new_plan_id(self, value):
#         try:
#             new_plan = SubscriptionPlan.objects.get(id=value, is_active=True)
#             return value
#         except SubscriptionPlan.DoesNotExist:
#             raise serializers.ValidationError("Noto'g'ri yoki nofaol subscription plani")
#
#     def validate(self, attrs):
#         user = self.context['request'].user
#
#         # Active subscription borligini tekshirish
#         current_subscription = UserSubscription.objects.filter(
#             user=user,
#             status='active'
#         ).first()
#
#         if not current_subscription:
#             raise serializers.ValidationError("Active subscription topilmadi")
#
#         new_plan = SubscriptionPlan.objects.get(id=attrs['new_plan_id'])
#
#         # Yangi plan qimmatroq bo'lishi kerak
#         if new_plan.price <= current_subscription.plan.price:
#             raise serializers.ValidationError("Yangi plan joriy plandan qimmatroq bo'lishi kerak")
#
#         return attrs
#
#
# class SubscriptionUsageSerializer(serializers.ModelSerializer):
#     plan_limits = serializers.SerializerMethodField()
#     usage_stats = serializers.SerializerMethodField()
#
#     class Meta:
#         model = UserSubscription
#         fields = ('tests_used_today', 'study_materials_used', 'plan_limits', 'usage_stats')
#
#     def get_plan_limits(self, obj):
#         if obj.plan:
#             return {
#                 'max_tests_per_day': obj.plan.max_tests_per_day,
#                 'max_study_materials': obj.plan.max_study_materials
#             }
#         return None
#
#     def get_usage_stats(self, obj):
#         if obj.plan:
#             return {
#                 'tests_remaining': max(0, obj.plan.max_tests_per_day - obj.tests_used_today),
#                 'study_materials_remaining': max(0, obj.plan.max_study_materials - obj.study_materials_used),
#                 'tests_usage_percentage': (obj.tests_used_today / obj.plan.max_tests_per_day * 100) if obj.plan.max_tests_per_day > 0 else 0,
#                 'study_materials_usage_percentage': (obj.study_materials_used / obj.plan.max_study_materials * 100) if obj.plan.max_study_materials > 0 else 0
#             }
#         return None
#
#
# class PaymentHistorySerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     plan_name = serializers.CharField(source='plan.name', read_only=True)
#
#     class Meta:
#         model = SubscriptionTransaction
#         fields = ('id', 'user_email', 'plan_name', 'transaction_type', 'amount',
#                  'payment_method', 'status', 'transaction_id', 'created_at')
#         read_only_fields = ('user', 'transaction_id', 'created_at')
