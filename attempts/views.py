from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema

from .serializers import UserDailyUsageSerializer
from .services import DailyUsageService


class TodayUsageView(generics.RetrieveAPIView):
    """
    Bugungi kunlik foydalanish statistikasi
    (vocab, writing, speaking va h.k.).
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserDailyUsageSerializer

    def get_object(self):
        return DailyUsageService.get_or_create_today_usage(
            self.request.user
        )

    @swagger_auto_schema(
        operation_description="Bugungi kunlik foydalanish statistikasi",
        responses={200: UserDailyUsageSerializer},
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)