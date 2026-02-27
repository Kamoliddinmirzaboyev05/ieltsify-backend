from django.urls import path

from .views import TodayUsageView

app_name = "attempts"

urlpatterns = [
    path("today-usage/", TodayUsageView.as_view(), name="today-usage"),
]


