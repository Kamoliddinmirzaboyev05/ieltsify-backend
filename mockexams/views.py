"""
Mock Exam API Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import MockExam, MockExamAttempt, MockExamResult
from .services import MockExamService
from accounts.permissions import IsAdminUser


# =====================================================
# USER ENDPOINTS
# =====================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mock_exam_list(request):
    """Mavjud mock imtihonlar ro'yxati."""
    exam_type = request.GET.get('exam_type')
    mock_type = request.GET.get('mock_type')

    mocks = MockExamService.get_available_mocks(request.user, exam_type, mock_type)
    data = [{
        'id': m.id,
        'title': m.title,
        'description': m.description,
        'exam_type': m.exam_type,
        'mock_type': m.mock_type,
        'difficulty': m.difficulty,
        'estimated_duration_minutes': m.estimated_duration_minutes,
        'is_premium': m.is_premium,
        'has_listening': m.listening_test is not None,
        'has_reading': m.reading_test is not None,
        'has_writing': m.writing_task1 is not None or m.writing_task2 is not None,
        'has_speaking': m.speaking_questions is not None,
    } for m in mocks]

    return Response({'success': True, 'data': data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mock_exam_detail(request, mock_id):
    """Mock imtihon tafsilotlari."""
    mock = get_object_or_404(MockExam, id=mock_id, status='published')
    data = {
        'id': mock.id,
        'title': mock.title,
        'description': mock.description,
        'exam_type': mock.exam_type,
        'mock_type': mock.mock_type,
        'difficulty': mock.difficulty,
        'estimated_duration_minutes': mock.estimated_duration_minutes,
        'speaking_questions': mock.speaking_questions,
    }
    return Response({'success': True, 'data': data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mock_access_status(request):
    """Foydalanuvchining mock exam quota va coin holati."""
    data = MockExamService.get_mock_access_status(request.user)
    return Response({'success': True, 'data': data})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mock_exam_start(request, mock_id):
    """Mock imtihonni boshlash."""
    access_source = request.data.get('access_source', 'subscription_quota')
    idempotency_key = request.data.get('idempotency_key')

    # Can start check
    can_start = MockExamService.can_start_mock(request.user, mock_id)
    if not can_start['allowed']:
        return Response({'success': False, **can_start}, status=status.HTTP_403_FORBIDDEN)

    try:
        attempt = MockExamService.start_mock(
            user=request.user,
            mock_id=mock_id,
            access_source=access_source,
            idempotency_key=idempotency_key,
        )
        return Response({
            'success': True,
            'data': {
                'attempt_id': attempt.id,
                'mock_type': attempt.mock_type,
                'exam_type': attempt.exam_type,
                'status': attempt.status,
                'started_at': attempt.started_at.isoformat(),
                'expires_at': attempt.expires_at.isoformat(),
                'current_section': attempt.current_section,
            }
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mock_active_attempt(request):
    """Foydalanuvchining aktiv attempt'ini olish."""
    attempt = MockExamAttempt.objects.filter(
        user=request.user,
        status__in=['in_progress', 'listening_completed', 'reading_completed', 'writing_completed', 'speaking_pending']
    ).first()

    if not attempt:
        return Response({'success': True, 'data': None})

    return Response({
        'success': True,
        'data': {
            'attempt_id': attempt.id,
            'mock_id': attempt.mock_exam_id,
            'mock_type': attempt.mock_type,
            'exam_type': attempt.exam_type,
            'status': attempt.status,
            'current_section': attempt.current_section,
            'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
            'expires_at': attempt.expires_at.isoformat() if attempt.expires_at else None,
        }
    })


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def mock_save_answers(request, attempt_id):
    """Javoblarni saqlash (auto-save)."""
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user)

    answers = request.data.get('answers', [])
    for ans in answers:
        MockExamService.save_answer(
            attempt_id=attempt.id,
            section_type=ans.get('section_type', 'reading'),
            question_number=ans.get('question_number', 0),
            answer=ans.get('answer', ''),
            is_flagged=ans.get('is_flagged', False),
        )

    return Response({'success': True, 'message': 'Javoblar saqlandi'})


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def mock_save_writing(request, attempt_id):
    """Writing draft saqlash."""
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user)

    task_type = request.data.get('task_type', 'task2')
    content = request.data.get('content', '')

    MockExamService.save_writing_draft(attempt.id, task_type, content)
    return Response({'success': True, 'message': 'Writing saqlandi', 'word_count': len(content.split())})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mock_complete_section(request, attempt_id, section):
    """Bo'limni yakunlash."""
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user)

    if section not in ['listening', 'reading', 'writing', 'speaking']:
        return Response({'success': False, 'error': 'Invalid section'}, status=400)

    attempt = MockExamService.complete_section(attempt.id, section)
    return Response({
        'success': True,
        'data': {
            'status': attempt.status,
            'current_section': attempt.current_section,
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mock_submit(request, attempt_id):
    """Mock imtihonni yakunlash."""
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user)

    if attempt.status == 'completed':
        return Response({'success': False, 'error': 'Already submitted'}, status=400)

    result = MockExamService.submit_mock(attempt.id)
    return Response({
        'success': True,
        'data': {
            'attempt_id': attempt.id,
            'status': 'completed',
            'overall_band': result.overall_band,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mock_attempt_result(request, attempt_id):
    """Attempt natijasi."""
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user)
    result = MockExamService.get_attempt_result(attempt.id)

    if not result:
        return Response({'success': False, 'error': 'Natija hali tayyor emas'}, status=404)

    return Response({
        'success': True,
        'data': {
            'attempt_id': attempt.id,
            'mock_type': attempt.mock_type,
            'exam_type': attempt.exam_type,
            'listening_band': result.listening_band,
            'reading_band': result.reading_band,
            'writing_band': result.writing_band,
            'speaking_band': result.speaking_band,
            'overall_band': result.overall_band,
            'skill_breakdown': result.skill_breakdown,
            'weak_skills': result.weak_skills,
            'strong_skills': result.strong_skills,
            'recommendations': result.recommendations,
            'question_type_accuracy': result.question_type_accuracy,
            'writing_task1_feedback': result.writing_task1_feedback,
            'writing_task2_feedback': result.writing_task2_feedback,
            'speaking_feedback': result.speaking_feedback,
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mock_attempt_history(request):
    """Foydalanuvchining mock attempt tarixi."""
    attempts = MockExamAttempt.objects.filter(
        user=request.user,
        status='completed'
    ).select_related('mock_exam').order_by('-completed_at')[:10]

    data = []
    for a in attempts:
        result = MockExamResult.objects.filter(attempt=a).first()
        data.append({
            'attempt_id': a.id,
            'mock_title': a.mock_exam.title,
            'mock_type': a.mock_type,
            'exam_type': a.exam_type,
            'overall_band': result.overall_band if result else None,
            'completed_at': a.completed_at.isoformat() if a.completed_at else None,
        })

    return Response({'success': True, 'data': data})


# =====================================================
# ADMIN ENDPOINTS
# =====================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_mock_list(request):
    """Admin: barcha mock imtihonlar."""
    mocks = MockExam.objects.all().order_by('-created_at')
    data = [{
        'id': m.id,
        'title': m.title,
        'exam_type': m.exam_type,
        'mock_type': m.mock_type,
        'difficulty': m.difficulty,
        'status': m.status,
        'attempts_count': m.attempts.count(),
        'created_at': m.created_at.isoformat(),
    } for m in mocks]
    return Response({'success': True, 'data': data})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_mock_create(request):
    """Admin: yangi mock yaratish."""
    data = request.data
    mock = MockExam.objects.create(
        title=data.get('title', ''),
        description=data.get('description', ''),
        exam_type=data.get('exam_type', 'academic'),
        mock_type=data.get('mock_type', 'core'),
        difficulty=data.get('difficulty', 'medium'),
        listening_test_id=data.get('listening_test_id'),
        reading_test_id=data.get('reading_test_id'),
        writing_task1_id=data.get('writing_task1_id'),
        writing_task2_id=data.get('writing_task2_id'),
        speaking_questions=data.get('speaking_questions'),
        estimated_duration_minutes=data.get('estimated_duration_minutes', 150),
        is_premium=data.get('is_premium', True),
        status=data.get('status', 'draft'),
        created_by=request.user,
    )
    return Response({'success': True, 'data': {'id': mock.id, 'title': mock.title}}, status=201)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_mock_publish(request, mock_id):
    """Admin: mock'ni publish qilish."""
    mock = get_object_or_404(MockExam, id=mock_id)
    mock.status = 'published'
    mock.save()
    return Response({'success': True, 'message': 'Mock published'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_mock_archive(request, mock_id):
    """Admin: mock'ni archive qilish."""
    mock = get_object_or_404(MockExam, id=mock_id)
    mock.status = 'archived'
    mock.save()
    return Response({'success': True, 'message': 'Mock archived'})
