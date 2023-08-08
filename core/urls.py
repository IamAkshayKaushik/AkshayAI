from django.urls import path
from django.views.generic import TemplateView

from .views import dashboard, buy_tokens, google_login, twitter_login, process_payment, create_convert_text_to_audio_task, convert_text_to_audio

urlpatterns = [
    path('', convert_text_to_audio, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('buy_tokens/', buy_tokens, name='buy_tokens'),
    path('login/google/', google_login, name='google_login'),
    path('login/twitter/', twitter_login, name='twitter_login'),
    path('process_payment/', process_payment, name='process_payment'),
    path('convert_text_to_audio/', convert_text_to_audio, name='convert_text_to_audio'),
    path('text-to-audio-task/', create_convert_text_to_audio_task, name='text-to-audio-task')
]
