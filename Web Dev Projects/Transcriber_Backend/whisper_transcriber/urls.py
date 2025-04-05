from django.urls import path
from .views import home, transcribe_audio, index

urlpatterns = [
    path("", index, name="home"),
    path("transcribe/", transcribe_audio, name="transcribe_audio"),
]