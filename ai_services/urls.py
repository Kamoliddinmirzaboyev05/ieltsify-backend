from django.urls import path
from .views import (
    writing_analyze, writing_result, writing_history,
    admin_ai_settings, admin_ai_usage,
)

app_name = 'ai_services'

urlpatterns = [
    # Writing AI
    path('writing/analyze/', writing_analyze, name='writing-analyze'),
    path('writing/submissions/<int:submission_id>/result/', writing_result, name='writing-result'),
    path('writing/history/', writing_history, name='writing-history'),

    # Admin AI
    path('admin-ai/settings/', admin_ai_settings, name='admin-ai-settings'),
    path('admin-ai/usage/', admin_ai_usage, name='admin-ai-usage'),
]
