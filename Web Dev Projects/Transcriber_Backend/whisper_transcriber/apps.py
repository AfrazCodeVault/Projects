from django.apps import AppConfig
import whisper
from together import Together

class WhisperTranscriberConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'whisper_transcriber'

    def ready(self):
        """Load the Whisper model when Django starts."""
        global whisper_model
        whisper_model = whisper.load_model("base")  # Load model once
        client = Together(api_key="40e99ab44b369b3bf108d547d07ef7d88fcfe9dc894051d89d4efba30065b2df")