from django.apps import AppConfig


class ModulesConfig(AppConfig):
    name = 'modules'

    def ready(self):
        # Signals ni ulash
        from . import signals  # noqa: F401