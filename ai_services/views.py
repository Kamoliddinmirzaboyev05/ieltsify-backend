"""
AI Services API Views — Writing va Speaking analyze endpointlari.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone

from .models import WritingSubmission, WritingAIFeedback, SpeakingAttempt, SpeakingTranscript, SpeakingAIFeedback, AIUsageLog
from .providers import get_writing_provider, get_speaking_provider, get_transcription_provider
from .config import AIConfig
from subscriptions.entitlement_service import EntitlementService, UsageLimitService
from subscriptions.services import WalletService
from accounts.permissions import IsAdminUser


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def writing_analyze(request):
    """Writing essay'ni AI orqali tahlil qilish."""
    task_type = request.data.get('task_type', 'task_2')
    question = request.data.get('question', '')
    essay = request.data.get('essay', '')
    writing_task_id = request.data.get('writing_task_id')
    use_coin = request.data.get('use_coin', False)

    if not essay or len(essay.strip()) < 50:
        return Response({'error': 'Essay kamida 50 ta belgidan iborat bo\'lishi kerak'}, status=400)

    # Entitlement check
    service_code = 'writing_task1' if task_type == 'task_1' else 'writing_task2'
    access = EntitlementService.can_use_writing_ai(request.user, service_code)

    if not access['allowed']:
        return Response({'error': access.get('message', 'Ruxsat yo\'q'), 'access': access}, status=403)

    # Coin yechish (agar kerak bo'lsa)
    coin_tx_id = None
    quota_source = 'subscription'
    if access.get('requires_coin'):
        if not use_coin:
            return Response({'requires_coin_confirmation': True, 'access': access}, status=402)
        try:
            wallet = WalletService.change_balance(
                user=request.user,
                amount=-access['required_coin'],
                tx_type='writing_evaluation',
                description=f'Writing {task_type} AI tahlili',
            )
            coin_tx_id = str(wallet.id)
            quota_source = 'coin'
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

    # Submission yaratish
    word_count = len(essay.split())
    submission = WritingSubmission.objects.create(
        user=request.user,
        writing_task_id=writing_task_id,
        task_type=task_type,
        content=essay,
        word_count=word_count,
        status='processing',
        quota_source=quota_source,
        coin_transaction_id=coin_tx_id,
    )

    # AI tahlil
    provider = get_writing_provider()
    result = provider.analyze_writing(task_type, question, essay)

    if result.get('status') == 'failed' or 'error' in result:
        # AI xato — refund
        submission.status = 'failed'
        submission.save()

        if coin_tx_id:
            WalletService.change_balance(
                user=request.user,
                amount=access['required_coin'],
                tx_type='manual_adjustment',
                description='Writing AI xatosi — refund',
            )

        return Response({'error': result.get('error', 'AI tahlilida xatolik'), 'submission_id': submission.id}, status=500)

    # Natijani saqlash
    meta = result.pop('_meta', {})
    feedback = WritingAIFeedback.objects.create(
        submission=submission,
        provider=meta.get('provider', 'unknown'),
        model=meta.get('model', 'unknown'),
        assessment_json=result,
        estimated_overall_band=result.get('estimatedOverallBand'),
        confidence=result.get('confidence'),
        processing_time_ms=meta.get('processing_time_ms', 0),
        status='success',
    )

    submission.status = 'completed'
    submission.save()

    # Usage increment
    UsageLimitService.increment_writing_ai(request.user)

    # Log
    AIUsageLog.objects.create(
        user=request.user,
        service_type=f'writing_{task_type}_analysis',
        provider=meta.get('provider', 'unknown'),
        model=meta.get('model', 'unknown'),
        reference_type='writing_submission',
        reference_id=str(submission.id),
        processing_time_ms=meta.get('processing_time_ms', 0),
        status='success',
    )

    return Response({
        'success': True,
        'data': {
            'submission_id': submission.id,
            'assessment': result,
            'overall_band': result.get('estimatedOverallBand'),
            'word_count': word_count,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def writing_result(request, submission_id):
    """Writing submission natijasini olish."""
    try:
        submission = WritingSubmission.objects.get(id=submission_id, user=request.user)
    except WritingSubmission.DoesNotExist:
        return Response({'error': 'Submission topilmadi'}, status=404)

    feedback = WritingAIFeedback.objects.filter(submission=submission).first()

    return Response({
        'success': True,
        'data': {
            'submission_id': submission.id,
            'task_type': submission.task_type,
            'word_count': submission.word_count,
            'status': submission.status,
            'assessment': feedback.assessment_json if feedback else None,
            'overall_band': feedback.estimated_overall_band if feedback else None,
            'confidence': feedback.confidence if feedback else None,
            'submitted_at': submission.submitted_at.isoformat(),
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def writing_history(request):
    """Foydalanuvchining Writing tahlil tarixi."""
    submissions = WritingSubmission.objects.filter(
        user=request.user, status='completed'
    ).order_by('-created_at')[:20]

    data = []
    for s in submissions:
        feedback = WritingAIFeedback.objects.filter(submission=s).first()
        data.append({
            'id': s.id,
            'task_type': s.task_type,
            'word_count': s.word_count,
            'overall_band': feedback.estimated_overall_band if feedback else None,
            'submitted_at': s.submitted_at.isoformat(),
        })

    return Response({'success': True, 'data': data})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_ai_settings(request):
    """Admin: AI provider status."""
    return Response({'success': True, 'data': AIConfig.get_status()})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_ai_usage(request):
    """Admin: AI usage summary."""
    from django.db.models import Count, Sum
    today = timezone.now().date()

    logs = AIUsageLog.objects.all()
    today_logs = logs.filter(created_at__date=today)

    summary = {
        'total_requests': logs.count(),
        'today_requests': today_logs.count(),
        'by_service': list(logs.values('service_type').annotate(count=Count('id')).order_by('-count')),
        'by_provider': list(logs.values('provider').annotate(count=Count('id')).order_by('-count')),
        'errors': logs.filter(status='failed').count(),
    }

    return Response({'success': True, 'data': summary})
