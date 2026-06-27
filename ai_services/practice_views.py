"""
Amaliyot (practice) sahifalari uchun AI gateway endpointlari.

Frontend (Speaking, Writing Simulator, Smart Article) avval Gemini'ni
to'g'ridan-to'g'ri chaqirar edi — API kalit brauzerда ochiq edi.
Endi shu endpointlar orqali, kalit faqat serverda saqlanadi.
"""
import json
import logging

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .providers import GeminiProvider, get_writing_provider

logger = logging.getLogger('ai_services')


def _strip_json(text: str) -> str:
    """Gemini javobidan ```json ... ``` markdown qobig'ini olib tashlash."""
    clean = (text or '').strip()
    if clean.startswith('```'):
        # birinchi qatordan keyin va oxirgi ``` gacha
        clean = clean.split('\n', 1)[-1]
        clean = clean.rsplit('```', 1)[0]
    return clean.strip()


def _gemini_json(prompt: str):
    """Promptни yuborib JSON javob qaytaradi yoki (None, error_response)."""
    result = GeminiProvider.generate_text(prompt, json_mode=True, temperature=0.3)
    if result.get('status') != 'success':
        return None, Response(
            {'error': result.get('error', 'AI xatolik')},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    try:
        return json.loads(_strip_json(result['text'])), None
    except json.JSONDecodeError:
        logger.error("Practice AI: JSON parse error")
        return None, Response(
            {'error': 'AI dan yaroqsiz javob keldi'},
            status=status.HTTP_502_BAD_GATEWAY,
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_chat(request):
    """Erkin matnli chat (Smart Article sahifasi uchun)."""
    prompt = (request.data.get('prompt') or '').strip()
    if not prompt:
        return Response({'error': 'prompt majburiy'}, status=status.HTTP_400_BAD_REQUEST)
    if len(prompt) > 8000:
        return Response({'error': 'prompt juda uzun'}, status=status.HTTP_400_BAD_REQUEST)

    result = GeminiProvider.generate_text(prompt, json_mode=False)
    if result.get('status') != 'success':
        return Response({'error': result.get('error', 'AI xatolik')}, status=status.HTTP_502_BAD_GATEWAY)
    return Response({'text': result['text']})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_evaluate_writing(request):
    """Bitta essayni baholash. Qaytadi: WritingEvaluation."""
    topic = (request.data.get('topic') or '').strip()
    essay = (request.data.get('essay') or '').strip()
    if not essay:
        return Response({'error': 'essay majburiy'}, status=status.HTTP_400_BAD_REQUEST)

    prompt = f'''Act as a strict IELTS Examiner. Evaluate the following essay for a given topic.
Topic: "{topic}"
Essay: "{essay}"

Evaluate based on: Task Response (TR), Coherence & Cohesion (CC), Lexical Resource (LR), Grammatical Range & Accuracy (GRA).

Return a JSON object STRICTLY with this structure:
{{
  "band_score": 6.5,
  "breakdown": {{ "TR": 6, "CC": 7, "LR": 6, "GRA": 7 }},
  "feedback": "...",
  "corrections": [
    {{ "original": "...", "correction": "...", "reason": "..." }}
  ]
}}
Do not include any other text before or after the JSON.'''

    data, err = _gemini_json(prompt)
    return err or Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_evaluate_speaking(request):
    """Speaking javobini baholash. Qaytadi: SpeakingEvaluation."""
    question = (request.data.get('question') or '').strip()
    transcript = (request.data.get('transcript') or '').strip()
    if not transcript:
        return Response({'error': 'transcript majburiy'}, status=status.HTTP_400_BAD_REQUEST)

    prompt = f'''Act as an IELTS Speaking Examiner. Evaluate the following response.
Question: "{question}"
Transcript: "{transcript}"

Return a JSON object STRICTLY with this structure:
{{
  "band_score": 7.0,
  "feedback": "...",
  "better_vocabulary": ["...", "..."]
}}
Do not include any other text before or after the JSON.'''

    data, err = _gemini_json(prompt)
    return err or Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_evaluate_full_writing(request):
    """Task 1 + Task 2 ni birga baholash. Qaytadi: WritingFullTestEvaluation."""
    t1q = (request.data.get('task1Question') or '').strip()
    t1e = (request.data.get('task1Essay') or '').strip()
    t2q = (request.data.get('task2Question') or '').strip()
    t2e = (request.data.get('task2Essay') or '').strip()
    if not t1e or not t2e:
        return Response(
            {'error': 'task1Essay va task2Essay majburiy'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    prompt = f'''Act as a professional IELTS Writing Examiner. Evaluate both Task 1 and Task 2 essays.

**TASK 1:**
Question: "{t1q}"
Essay: "{t1e}"

**TASK 2:**
Question: "{t2q}"
Essay: "{t2e}"

Evaluate each task based on IELTS criteria:
- Task 1: Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy
- Task 2: Task Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy

Return a JSON object STRICTLY with this structure:
{{
  "task1Score": 7.0,
  "task1Feedback": "Detailed professional feedback for Task 1 (minimum 150 words).",
  "task2Score": 7.5,
  "task2Feedback": "Detailed professional feedback for Task 2 (minimum 200 words).",
  "overallScore": 7.0,
  "overallFeedback": "Overall assessment combining both tasks (minimum 100 words)."
}}

IMPORTANT:
- Scores must be realistic IELTS band scores in 0.5 increments
- Overall score is the average of Task 1 and Task 2
- Do not include any text before or after the JSON'''

    data, err = _gemini_json(prompt)
    return err or Response(data)
