from django.urls import path
from .views import (
    writing_analyze, writing_result, writing_history,
    admin_ai_settings, admin_ai_usage,
)
from .practice_views import (
    ai_chat, ai_evaluate_writing, ai_evaluate_speaking, ai_evaluate_full_writing,
)

app_name = 'ai_services'

urlpatterns = [
    # Writing AI
    path('writing/analyze/', writing_analyze, name='writing-analyze'),
    path('writing/submissions/<int:submission_id>/result/', writing_result, name='writing-result'),
    path('writing/history/', writing_history, name='writing-history'),

    # Practice AI gateway (frontend Gemini proxy)
    path('chat/', ai_chat, name='ai-chat'),
    path('evaluate-writing/', ai_evaluate_writing, name='ai-evaluate-writing'),
    path('evaluate-speaking/', ai_evaluate_speaking, name='ai-evaluate-speaking'),
    path('evaluate-full-writing/', ai_evaluate_full_writing, name='ai-evaluate-full-writing'),

    # Admin AI
    path('admin-ai/settings/', admin_ai_settings, name='admin-ai-settings'),
    path('admin-ai/usage/', admin_ai_usage, name='admin-ai-usage'),
]
