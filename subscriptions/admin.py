from django.contrib import admin
from django.utils.html import format_html

from .models import (
    SubscriptionPlan,
    UserSubscription,
    CoinWallet,
    CoinTransaction,
    CoinPack,
    Payment,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "price_uzs",
        "duration_days",
        "included_coins",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "is_unlimited_reading", "is_unlimited_listening")
    search_fields = ("name", "code")
    ordering = ("price_uzs",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("code", "name", "description"),
        }),
        ("Narx va davomiylik", {
            "fields": ("price_uzs", "duration_days", "included_coins"),
        }),
        ("Limitlar", {
            "fields": (
                "is_unlimited_reading",
                "is_unlimited_listening",
                "is_unlimited_vocab",
                "daily_vocab_limit",
            ),
        }),
        ("Holat", {
            "fields": ("is_active",),
        }),
        ("Tizim", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "start_at",
        "end_at",
        "colored_status",
        "is_current",
    )
    list_filter = ("is_active", "auto_renew", "plan")
    search_fields = ("user__email",)
    autocomplete_fields = ("user", "plan")
    readonly_fields = ("created_at", "updated_at", "is_current")
    date_hierarchy = "start_at"
    list_select_related = ("user", "plan")

    fieldsets = (
        ("Foydalanuvchi", {
            "fields": ("user", "plan"),
        }),
        ("Muddat", {
            "fields": ("start_at", "end_at"),
        }),
        ("Holat", {
            "fields": ("is_active", "auto_renew", "is_current"),
        }),
        ("Tizim", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def colored_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">● Active</span>')
        return format_html('<span style="color:red;">● Inactive</span>')

    colored_status.short_description = "Status"


class CoinTransactionInline(admin.TabularInline):
    model = CoinTransaction
    extra = 0
    readonly_fields = (
        "amount",
        "type",
        "description",
        "created_at",
    )
    can_delete = False


@admin.register(CoinWallet)
class CoinWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")
    search_fields = ("user__email",)
    autocomplete_fields = ("user",)
    readonly_fields = ("updated_at",)
    inlines = [CoinTransactionInline]


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "type",
        "created_at",
    )
    list_filter = ("type",)
    search_fields = (
        "user__email",
        "description",
        "related_object_id",
    )
    autocomplete_fields = ("user", "wallet")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user", "wallet")


@admin.register(CoinPack)
class CoinPackAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "coins",
        "price_uzs",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "provider",
        "amount_uzs",
        "plan",
        "coin_pack",
        "colored_status",
        "created_at",
    )
    list_filter = ("provider", "status")
    search_fields = (
        "user__email",
        "provider_payment_id",
    )
    autocomplete_fields = ("user", "plan", "coin_pack")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    list_select_related = ("user", "plan", "coin_pack")

    fieldsets = (
        ("Foydalanuvchi", {
            "fields": ("user",),
        }),
        ("To'lov obyekti", {
            "fields": ("plan", "coin_pack"),
        }),
        ("Provayder", {
            "fields": (
                "provider",
                "provider_payment_id",
                "amount_uzs",
                "status",
            ),
        }),
        ("Qo'shimcha", {
            "fields": ("extra_data",),
        }),
        ("Tizim", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def colored_status(self, obj):
        colors = {
            "pending": "orange",
            "paid": "green",
            "failed": "red",
            "canceled": "gray",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.status.upper(),
        )

    colored_status.short_description = "Status"
