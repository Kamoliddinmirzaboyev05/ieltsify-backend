from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from .models import UserDailyUsage


@admin.register(UserDailyUsage)
class UserDailyUsageAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date",
        "vocab_learned_count",
        "writing_evaluation_count",
        "speaking_mock_count",
        "reading_attempt_count",
        "listening_attempt_count",
        "total_activity",
    )

    list_filter = (
        "date",
    )

    search_fields = (
        "user__email",
    )

    autocomplete_fields = (
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "total_activity",
    )

    date_hierarchy = "date"

    list_select_related = ("user",)

    ordering = ("-date",)

    fieldsets = (
        ("Foydalanuvchi", {
            "fields": ("user", "date"),
        }),
        ("Kunlik statistika", {
            "fields": (
                "vocab_learned_count",
                "writing_evaluation_count",
                "speaking_mock_count",
                "reading_attempt_count",
                "listening_attempt_count",
                "total_activity",
            ),
        }),
        ("Tizim", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def total_activity(self, obj):
        total = (
            obj.vocab_learned_count
            + obj.writing_evaluation_count
            + obj.speaking_mock_count
            + obj.reading_attempt_count
            + obj.listening_attempt_count
        )
        return format_html(
            '<strong style="color: #2c3e50;">{}</strong>',
            total
        )

    total_activity.short_description = "Total Activity"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")