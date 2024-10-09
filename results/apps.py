from django.apps import AppConfig

class ResultsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'results'

    def ready(self):
        # Import signals here to ensure they are loaded
        import results.signals
