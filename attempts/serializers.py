from rest_framework import serializers

from .models import UserDailyUsage


class UserDailyUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDailyUsage
        fields = (
            "date",
            "vocab_learned_count",
            "writing_evaluation_count",
            "speaking_mock_count",
            "reading_attempt_count",
            "listening_attempt_count",
        )


