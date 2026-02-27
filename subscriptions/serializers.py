from rest_framework import serializers

from .models import (
    SubscriptionPlan,
    UserSubscription,
    CoinWallet,
    CoinTransaction,
    CoinPack,
    Payment,
)


class SubscriptionPlanReadSerializer(serializers.ModelSerializer):
    duration_label = serializers.SerializerMethodField()
    price_per_day = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "code",
            "name",
            "description",
            "price_uzs",
            "duration_days",
            "duration_label",
            "price_per_day",
            "included_coins",
            "is_unlimited_reading",
            "is_unlimited_listening",
            "is_unlimited_vocab",
            "daily_vocab_limit",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_duration_label(self, obj):
        if obj.duration_days == 7:
            return "Weekly"
        elif obj.duration_days == 30:
            return "Monthly"
        return f"{obj.duration_days} days"

    def get_price_per_day(self, obj):
        if obj.duration_days > 0:
            return obj.price_uzs / obj.duration_days
        return 0


class SubscriptionPlanWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "code",
            "name",
            "description",
            "price_uzs",
            "duration_days",
            "included_coins",
            "is_unlimited_reading",
            "is_unlimited_listening",
            "is_unlimited_vocab",
            "daily_vocab_limit",
            "is_active",
        ]

    def validate_price_uzs(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo‘lishi kerak.")
        return value

    def validate_duration_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration kamida 1 kun bo‘lishi kerak.")
        return value

    def validate(self, attrs):
        """
        Biznes qoidalar:
        - Agar unlimited_vocab=True bo‘lsa daily_vocab_limit None bo‘lishi kerak
        - Agar unlimited_vocab=False bo‘lsa daily_vocab_limit majburiy
        """

        is_unlimited_vocab = attrs.get("is_unlimited_vocab")
        daily_vocab_limit = attrs.get("daily_vocab_limit")

        if is_unlimited_vocab:
            attrs["daily_vocab_limit"] = None
        else:
            if not daily_vocab_limit:
                raise serializers.ValidationError(
                    {"daily_vocab_limit": "Cheklangan tarif uchun daily_vocab_limit majburiy."}
                )

        return attrs

    def create(self, validated_data):
        return SubscriptionPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CoinPackReadSerializer(serializers.ModelSerializer):
    price_per_coin = serializers.SerializerMethodField()
    display_label = serializers.SerializerMethodField()

    class Meta:
        model = CoinPack
        fields = [
            "id",
            "name",
            "coins",
            "price_uzs",
            "price_per_coin",
            "display_label",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_price_per_coin(self, obj):
        if obj.coins > 0:
            return round(obj.price_uzs / obj.coins, 2)
        return 0

    def get_display_label(self, obj):
        return f"{obj.coins} Coin - {obj.price_uzs:,} UZS"


class CoinPackWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinPack
        fields = [
            "name",
            "coins",
            "price_uzs",
            "is_active",
        ]

    def validate_name(self, value):
        if CoinPack.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Bu nomli CoinPack allaqachon mavjud.")
        return value

    def validate_coins(self, value):
        if value <= 0:
            raise serializers.ValidationError("Coin miqdori 0 dan katta bo‘lishi kerak.")
        return value

    def validate_price_uzs(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo‘lishi kerak.")
        return value

    def create(self, validated_data):
        return CoinPack.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanReadSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "plan",
            "start_at",
            "end_at",
            "is_active",
            "auto_renew",
        )


class CoinWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinWallet
        fields = (
            "balance",
            "updated_at",
        )


class CoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTransaction
        fields = (
            "id",
            "amount",
            "type",
            "description",
            "related_object_id",
            "related_object_type",
            "created_at",
        )


class CreateSubscriptionPaymentSerializer(serializers.Serializer):
    """
    Foydalanuvchi tanlagan plan bo'yicha to'lov yaratish uchun serializer.
    Frontend:
    - plan_id
    - provider (click/payme)
    yuboradi.
    """

    plan_id = serializers.IntegerField()
    provider = serializers.ChoiceField(
        choices=[(Payment.PROVIDER_CLICK, "click"), (Payment.PROVIDER_PAYME, "payme")]
    )


class CreateCoinPackPaymentSerializer(serializers.Serializer):
    coin_pack_id = serializers.IntegerField()
    provider = serializers.ChoiceField(
        choices=[(Payment.PROVIDER_CLICK, "click"), (Payment.PROVIDER_PAYME, "payme")]
    )


class PaymentSerializer(serializers.ModelSerializer):
    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "plan",
            "coin_pack",
            "provider",
            "provider_payment_id",
            "amount_uzs",
            "status",
            "payment_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "user",
            "amount_uzs",
            "status",
            "payment_url",
            "created_at",
            "updated_at",
        )

    def get_payment_url(self, obj):
        """To'lov URL ni qaytarish"""
        return getattr(obj, 'payment_url', None)


class PaymentCallbackSerializer(serializers.Serializer):
    """
    Click/Payme callback uchun umumiy serializer.
    Bu yerda siz o'zingizning real integratsiya maydonlaringizni qo'shib ketishingiz mumkin.
    Hozircha minimal maydonlar:
    - payment_id (bizning tizimdagi Payment.id yoki provider_payment_id)
    - status (paid/failed/canceled)
    - provider_payment_id (provayderdan kelgan ID)
    """

    payment_id = serializers.IntegerField(required=False)
    status = serializers.ChoiceField(
        choices=[
            (Payment.STATUS_PAID, "paid"),
            (Payment.STATUS_FAILED, "failed"),
            (Payment.STATUS_CANCELED, "canceled"),
        ]
    )
    provider_payment_id = serializers.CharField(required=False, allow_blank=True)
