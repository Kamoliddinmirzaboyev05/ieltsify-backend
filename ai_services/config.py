"""
AI Services Configuration — .env dan o'qiladi va validatsiya qilinadi.
"""
import os
import logging

logger = logging.getLogger('ai_services')


class AIConfig:
    """AI provider konfiguratsiyasi."""

    # Google Gemini
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', '')
    GEMINI_WRITING_PRIMARY_MODEL = os.getenv('GEMINI_WRITING_PRIMARY_MODEL', 'gemini-2.5-flash')
    GEMINI_WRITING_PRE_ANALYSIS_MODEL = os.getenv('GEMINI_WRITING_PRE_ANALYSIS_MODEL', 'gemini-2.5-flash-lite')
    GEMINI_SPEAKING_ASSESSMENT_MODEL = os.getenv('GEMINI_SPEAKING_ASSESSMENT_MODEL', 'gemini-2.5-flash')
    GEMINI_MOCK_REPORT_MODEL = os.getenv('GEMINI_MOCK_REPORT_MODEL', 'gemini-2.5-flash')
    GEMINI_ENABLED = os.getenv('GEMINI_ENABLED', 'true').lower() == 'true'

    # Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_STT_PRIMARY_MODEL = os.getenv('GROQ_STT_PRIMARY_MODEL', 'whisper-large-v3-turbo')
    GROQ_STT_FALLBACK_MODEL = os.getenv('GROQ_STT_FALLBACK_MODEL', 'whisper-large-v3')
    GROQ_STT_ENABLED = os.getenv('GROQ_STT_ENABLED', 'true').lower() == 'true'

    # Azure
    AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY', '')
    AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION', '')
    AZURE_PRONUNCIATION_ENABLED = os.getenv('AZURE_PRONUNCIATION_ENABLED', 'false').lower() == 'true'

    # Anthropic
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_FALLBACK_MODEL = os.getenv('ANTHROPIC_FALLBACK_MODEL', 'claude-haiku-4-20250514')
    ANTHROPIC_FALLBACK_ENABLED = os.getenv('ANTHROPIC_FALLBACK_ENABLED', 'false').lower() == 'true'

    # Behavior
    AI_PROVIDER_TIMEOUT_MS = int(os.getenv('AI_PROVIDER_TIMEOUT_MS', '45000'))
    AI_MAX_RETRY_COUNT = int(os.getenv('AI_MAX_RETRY_COUNT', '2'))
    AI_FALLBACK_ENABLED = os.getenv('AI_FALLBACK_ENABLED', 'true').lower() == 'true'
    AI_DEBUG_MODE = os.getenv('AI_DEBUG_MODE', 'false').lower() == 'true'

    @classmethod
    def validate(cls):
        """Startup'da konfiguratsiyani tekshirish."""
        warnings = []

        if not cls.GOOGLE_AI_API_KEY:
            warnings.append('⚠️  GOOGLE_AI_API_KEY missing — Writing/Speaking AI will not work')

        if not cls.GROQ_API_KEY:
            warnings.append('⚠️  GROQ_API_KEY missing — Speaking transcription will not work')

        if not cls.AZURE_SPEECH_KEY or not cls.AZURE_SPEECH_REGION:
            warnings.append('ℹ️  Azure Speech not configured — Pronunciation assessment disabled')
            cls.AZURE_PRONUNCIATION_ENABLED = False

        if not cls.ANTHROPIC_API_KEY:
            warnings.append('ℹ️  ANTHROPIC_API_KEY missing — Fallback disabled')
            cls.ANTHROPIC_FALLBACK_ENABLED = False

        for w in warnings:
            logger.warning(w)
            print(w)

        return warnings

    @classmethod
    def get_status(cls):
        """Admin panel uchun provider status."""
        return {
            'gemini': {
                'configured': bool(cls.GOOGLE_AI_API_KEY),
                'enabled': cls.GEMINI_ENABLED,
                'writing_model': cls.GEMINI_WRITING_PRIMARY_MODEL,
                'speaking_model': cls.GEMINI_SPEAKING_ASSESSMENT_MODEL,
            },
            'groq': {
                'configured': bool(cls.GROQ_API_KEY),
                'enabled': cls.GROQ_STT_ENABLED,
                'primary_model': cls.GROQ_STT_PRIMARY_MODEL,
            },
            'azure': {
                'configured': bool(cls.AZURE_SPEECH_KEY and cls.AZURE_SPEECH_REGION),
                'enabled': cls.AZURE_PRONUNCIATION_ENABLED,
            },
            'anthropic': {
                'configured': bool(cls.ANTHROPIC_API_KEY),
                'enabled': cls.ANTHROPIC_FALLBACK_ENABLED,
                'model': cls.ANTHROPIC_FALLBACK_MODEL,
            },
        }
