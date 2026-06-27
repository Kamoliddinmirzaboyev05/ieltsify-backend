"""
AI Provider Adapters — Gemini, Groq, Azure, Anthropic
"""
import json
import time
import logging
import requests
from typing import Optional
from .config import AIConfig

logger = logging.getLogger('ai_services')


class GeminiProvider:
    """Google Gemini API provider for Writing/Speaking assessment."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    @classmethod
    def generate_text(cls, prompt: str, json_mode: bool = False, temperature: float = 0.4) -> dict:
        """Umumiy Gemini matn generatsiyasi (chat va baholash uchun).

        Qaytadi: {'text': str, 'status': 'success'} yoki {'error': str, 'status': 'failed'}.
        Kalit faqat shu yerda (serverda) ishlatiladi — frontendга chiqmaydi.
        """
        if not AIConfig.GOOGLE_AI_API_KEY:
            return {'error': 'Gemini API key not configured', 'status': 'failed'}

        model = AIConfig.GEMINI_WRITING_PRIMARY_MODEL
        generation_config = {
            "temperature": temperature,
            "maxOutputTokens": 4096,
        }
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        try:
            url = f"{cls.BASE_URL}/{model}:generateContent?key={AIConfig.GOOGLE_AI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": generation_config,
            }
            response = requests.post(url, json=payload, timeout=AIConfig.AI_PROVIDER_TIMEOUT_MS / 1000)

            if response.status_code != 200:
                logger.error(f"Gemini error: {response.status_code} - {response.text[:200]}")
                return {'error': f'Gemini API error: {response.status_code}', 'status': 'failed'}

            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            return {'text': text, 'status': 'success'}

        except requests.Timeout:
            return {'error': 'AI request timeout', 'status': 'failed'}
        except (KeyError, IndexError) as e:
            logger.error(f"Gemini response shape error: {e}")
            return {'error': 'Unexpected AI response', 'status': 'failed'}
        except Exception as e:
            logger.error(f"Gemini generate_text error: {e}")
            return {'error': str(e), 'status': 'failed'}

    @classmethod
    def analyze_writing(cls, task_type: str, question: str, essay: str, image_url: str = None) -> dict:
        """Writing essay'ni Gemini orqali baholash."""
        if not AIConfig.GOOGLE_AI_API_KEY:
            return {'error': 'Gemini API key not configured', 'status': 'failed'}

        model = AIConfig.GEMINI_WRITING_PRIMARY_MODEL
        prompt = cls._build_writing_prompt(task_type, question, essay)

        start_time = time.time()
        try:
            url = f"{cls.BASE_URL}/{model}:generateContent?key={AIConfig.GOOGLE_AI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 4096,
                    "responseMimeType": "application/json",
                }
            }

            response = requests.post(url, json=payload, timeout=AIConfig.AI_PROVIDER_TIMEOUT_MS / 1000)
            processing_time = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                logger.error(f"Gemini error: {response.status_code} - {response.text[:200]}")
                return {'error': f'Gemini API error: {response.status_code}', 'status': 'failed'}

            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']

            # Parse JSON from response
            clean_json = text.strip()
            if clean_json.startswith('```'):
                clean_json = clean_json.split('\n', 1)[1].rsplit('```', 1)[0]

            result = json.loads(clean_json)
            result['_meta'] = {
                'provider': 'gemini',
                'model': model,
                'processing_time_ms': processing_time,
                'status': 'success',
            }
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Gemini JSON parse error: {e}")
            return {'error': 'Invalid JSON response from AI', 'status': 'failed'}
        except requests.Timeout:
            return {'error': 'AI request timeout', 'status': 'failed'}
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {'error': str(e), 'status': 'failed'}

    @classmethod
    def analyze_speaking(cls, questions: list, transcript: str, audio_metrics: dict = None) -> dict:
        """Speaking transcript'ni Gemini orqali baholash."""
        if not AIConfig.GOOGLE_AI_API_KEY:
            return {'error': 'Gemini API key not configured', 'status': 'failed'}

        model = AIConfig.GEMINI_SPEAKING_ASSESSMENT_MODEL
        prompt = cls._build_speaking_prompt(questions, transcript, audio_metrics)

        start_time = time.time()
        try:
            url = f"{cls.BASE_URL}/{model}:generateContent?key={AIConfig.GOOGLE_AI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 4096,
                    "responseMimeType": "application/json",
                }
            }

            response = requests.post(url, json=payload, timeout=AIConfig.AI_PROVIDER_TIMEOUT_MS / 1000)
            processing_time = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                return {'error': f'Gemini API error: {response.status_code}', 'status': 'failed'}

            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            clean_json = text.strip()
            if clean_json.startswith('```'):
                clean_json = clean_json.split('\n', 1)[1].rsplit('```', 1)[0]

            result = json.loads(clean_json)
            result['_meta'] = {
                'provider': 'gemini',
                'model': model,
                'processing_time_ms': processing_time,
                'status': 'success',
            }
            return result

        except Exception as e:
            logger.error(f"Gemini Speaking error: {e}")
            return {'error': str(e), 'status': 'failed'}

    @classmethod
    def _build_writing_prompt(cls, task_type: str, question: str, essay: str) -> str:
        criteria_name = "Task Achievement" if "task_1" in task_type else "Task Response"
        return f"""You are a strict IELTS Writing examiner. Evaluate the following IELTS {task_type.replace('_', ' ').title()} essay.

Question: {question}

Essay: {essay}

Evaluate based on official IELTS criteria:
1. {criteria_name} (TR/TA)
2. Coherence and Cohesion (CC)
3. Lexical Resource (LR)
4. Grammatical Range and Accuracy (GRA)

Return a JSON object with this exact structure:
{{
  "assessmentType": "{task_type}",
  "estimatedOverallBand": 6.0,
  "confidence": 0.8,
  "criteria": {{
    "taskResponse": {{"band": 6.0, "reason": "...", "evidence": [], "recommendations": []}},
    "coherenceAndCohesion": {{"band": 6.0, "reason": "...", "evidence": [], "recommendations": []}},
    "lexicalResource": {{"band": 6.0, "reason": "...", "evidence": [], "recommendations": []}},
    "grammaticalRangeAndAccuracy": {{"band": 5.5, "reason": "...", "evidence": [], "recommendations": []}}
  }},
  "wordCount": 0,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "grammarErrors": [{{"original": "...", "corrected": "...", "explanation": "...", "severity": "minor"}}],
  "vocabularyIssues": [{{"original": "...", "suggestion": "...", "explanation": "..."}}],
  "repeatedWords": ["..."],
  "improvedSentences": [{{"original": "...", "improved": "...", "reason": "..."}}],
  "nextPracticeRecommendation": {{"skill": "...", "topic": "...", "reason": "..."}}
}}

Important:
- Band scores must be in 0.5 increments (5.0, 5.5, 6.0, 6.5, etc.)
- Overall band is the average of 4 criteria rounded to nearest 0.5
- Be strict but fair
- Provide specific evidence from the essay
- Give feedback in Uzbek language
- Count actual words in the essay for wordCount
- Do not include any text outside the JSON"""

    @classmethod
    def _build_speaking_prompt(cls, questions: list, transcript: str, audio_metrics: dict = None) -> str:
        metrics_text = ""
        if audio_metrics:
            metrics_text = f"""
Audio metrics:
- Duration: {audio_metrics.get('duration_seconds', 0)} seconds
- Word count: {audio_metrics.get('word_count', 0)}
- Words per minute: {audio_metrics.get('wpm', 0)}
- Pause count: {audio_metrics.get('pause_count', 0)}
"""

        return f"""You are a strict IELTS Speaking examiner. Evaluate the following speaking response.

Questions asked: {json.dumps(questions, ensure_ascii=False)}

Transcript: {transcript}
{metrics_text}

Evaluate based on IELTS Speaking criteria:
1. Fluency and Coherence
2. Lexical Resource
3. Grammatical Range and Accuracy
4. Pronunciation (based on transcript analysis only)

Return JSON:
{{
  "assessmentType": "speaking",
  "estimatedOverallBand": 6.0,
  "confidence": 0.75,
  "criteria": {{
    "fluencyAndCoherence": {{"band": 6.0, "reason": "...", "recommendations": []}},
    "lexicalResource": {{"band": 5.5, "reason": "...", "recommendations": []}},
    "grammaticalRangeAndAccuracy": {{"band": 5.5, "reason": "...", "recommendations": []}},
    "pronunciation": {{"band": 6.0, "isAvailable": false, "reason": "...", "recommendations": []}}
  }},
  "audioMetrics": {{"durationSeconds": 0, "wordCount": 0, "wordsPerMinute": 0}},
  "fillerWords": [],
  "repeatedWords": [],
  "grammarIssues": [],
  "strengths": [],
  "weaknesses": [],
  "nextPracticeRecommendation": {{"skill": "...", "topic": "...", "reason": "..."}}
}}

Give feedback in Uzbek language. Band scores in 0.5 increments."""


class GroqProvider:
    """Groq API for speech-to-text transcription."""

    BASE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

    @classmethod
    def transcribe(cls, audio_file_path: str, use_fallback: bool = False) -> dict:
        """Audio faylni transcribe qilish."""
        if not AIConfig.GROQ_API_KEY:
            return {'error': 'Groq API key not configured', 'status': 'failed'}

        model = AIConfig.GROQ_STT_FALLBACK_MODEL if use_fallback else AIConfig.GROQ_STT_PRIMARY_MODEL

        start_time = time.time()
        try:
            with open(audio_file_path, 'rb') as f:
                response = requests.post(
                    cls.BASE_URL,
                    headers={'Authorization': f'Bearer {AIConfig.GROQ_API_KEY}'},
                    files={'file': f},
                    data={
                        'model': model,
                        'language': 'en',
                        'response_format': 'verbose_json',
                    },
                    timeout=60,
                )

            processing_time = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                return {'error': f'Groq error: {response.status_code}', 'status': 'failed'}

            data = response.json()
            return {
                'transcript': data.get('text', ''),
                'segments': data.get('segments', []),
                'language': data.get('language', 'en'),
                'duration': data.get('duration', 0),
                '_meta': {
                    'provider': 'groq',
                    'model': model,
                    'processing_time_ms': processing_time,
                    'fallback_used': use_fallback,
                    'status': 'success',
                }
            }

        except Exception as e:
            logger.error(f"Groq transcription error: {e}")
            return {'error': str(e), 'status': 'failed'}


class MockAIProvider:
    """Development/testing uchun mock provider."""

    @classmethod
    def analyze_writing(cls, task_type: str, question: str, essay: str, **kwargs) -> dict:
        word_count = len(essay.split()) if essay else 0
        return {
            'assessmentType': task_type,
            'estimatedOverallBand': 6.0,
            'confidence': 0.5,
            'criteria': {
                'taskResponse': {'band': 6.0, 'reason': 'Mock assessment', 'evidence': [], 'recommendations': ['Practice more']},
                'coherenceAndCohesion': {'band': 6.0, 'reason': 'Mock assessment', 'evidence': [], 'recommendations': []},
                'lexicalResource': {'band': 5.5, 'reason': 'Mock assessment', 'evidence': [], 'recommendations': []},
                'grammaticalRangeAndAccuracy': {'band': 5.5, 'reason': 'Mock assessment', 'evidence': [], 'recommendations': []},
            },
            'wordCount': word_count,
            'strengths': ['Clear structure'],
            'weaknesses': ['Limited vocabulary'],
            'grammarErrors': [],
            'vocabularyIssues': [],
            'repeatedWords': [],
            'improvedSentences': [],
            'nextPracticeRecommendation': {'skill': 'writing', 'topic': 'grammar', 'reason': 'Improve accuracy'},
            '_meta': {'provider': 'mock', 'model': 'mock-v1', 'processing_time_ms': 100, 'status': 'success'},
        }

    @classmethod
    def analyze_speaking(cls, questions: list, transcript: str, **kwargs) -> dict:
        return {
            'assessmentType': 'speaking',
            'estimatedOverallBand': 6.0,
            'confidence': 0.5,
            'criteria': {
                'fluencyAndCoherence': {'band': 6.0, 'reason': 'Mock', 'recommendations': []},
                'lexicalResource': {'band': 5.5, 'reason': 'Mock', 'recommendations': []},
                'grammaticalRangeAndAccuracy': {'band': 5.5, 'reason': 'Mock', 'recommendations': []},
                'pronunciation': {'band': None, 'isAvailable': False, 'reason': 'Mock mode', 'recommendations': []},
            },
            'audioMetrics': {'durationSeconds': 60, 'wordCount': 100, 'wordsPerMinute': 100},
            'fillerWords': [],
            'repeatedWords': [],
            'grammarIssues': [],
            'strengths': ['Good attempt'],
            'weaknesses': ['Need more practice'],
            'nextPracticeRecommendation': {'skill': 'speaking', 'topic': 'fluency', 'reason': 'Practice daily'},
            '_meta': {'provider': 'mock', 'model': 'mock-v1', 'processing_time_ms': 50, 'status': 'success'},
        }

    @classmethod
    def transcribe(cls, audio_file_path: str, **kwargs) -> dict:
        return {
            'transcript': 'This is a mock transcript for testing purposes.',
            'segments': [],
            'language': 'en',
            'duration': 60,
            '_meta': {'provider': 'mock', 'model': 'mock-whisper', 'processing_time_ms': 50, 'fallback_used': False, 'status': 'success'},
        }


def get_writing_provider():
    """Writing AI provider olish — Gemini yoki Mock."""
    if AIConfig.GOOGLE_AI_API_KEY and AIConfig.GEMINI_ENABLED:
        return GeminiProvider
    return MockAIProvider


def get_speaking_provider():
    """Speaking AI provider olish — Gemini yoki Mock."""
    if AIConfig.GOOGLE_AI_API_KEY and AIConfig.GEMINI_ENABLED:
        return GeminiProvider
    return MockAIProvider


def get_transcription_provider():
    """Transcription provider olish — Groq yoki Mock."""
    if AIConfig.GROQ_API_KEY and AIConfig.GROQ_STT_ENABLED:
        return GroqProvider
    return MockAIProvider
