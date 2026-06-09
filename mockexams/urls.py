from django.urls import path
from .views import (
    mock_exam_list, mock_exam_detail, mock_access_status,
    mock_exam_start, mock_active_attempt,
    mock_save_answers, mock_save_writing,
    mock_complete_section, mock_submit,
    mock_attempt_result, mock_attempt_history,
    admin_mock_list, admin_mock_create,
    admin_mock_publish, admin_mock_archive,
)

app_name = 'mockexams'

urlpatterns = [
    # User endpoints
    path('mock-exams/', mock_exam_list, name='mock-list'),
    path('mock-exams/access-status/', mock_access_status, name='mock-access-status'),
    path('mock-exams/active-attempt/', mock_active_attempt, name='mock-active-attempt'),
    path('mock-exams/<int:mock_id>/', mock_exam_detail, name='mock-detail'),
    path('mock-exams/<int:mock_id>/start/', mock_exam_start, name='mock-start'),

    # Attempt endpoints
    path('mock-attempts/<int:attempt_id>/answers/', mock_save_answers, name='mock-save-answers'),
    path('mock-attempts/<int:attempt_id>/writing-draft/', mock_save_writing, name='mock-save-writing'),
    path('mock-attempts/<int:attempt_id>/sections/<str:section>/complete/', mock_complete_section, name='mock-complete-section'),
    path('mock-attempts/<int:attempt_id>/submit/', mock_submit, name='mock-submit'),
    path('mock-attempts/<int:attempt_id>/result/', mock_attempt_result, name='mock-result'),
    path('mock-attempts/history/', mock_attempt_history, name='mock-history'),

    # Admin endpoints
    path('admin-mock-exams/', admin_mock_list, name='admin-mock-list'),
    path('admin-mock-exams/create/', admin_mock_create, name='admin-mock-create'),
    path('admin-mock-exams/<int:mock_id>/publish/', admin_mock_publish, name='admin-mock-publish'),
    path('admin-mock-exams/<int:mock_id>/archive/', admin_mock_archive, name='admin-mock-archive'),
]
