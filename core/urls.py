from django.urls import path
from django.views.generic import TemplateView

from .views import dashboard, buy_tokens, google_login, twitter_login, process_payment

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='home'),
    path('buy_tokens/', buy_tokens, name='buy_tokens'),
    path('login/google/', google_login, name='google_login'),
    path('login/twitter/', twitter_login, name='twitter_login'),
    path('process_payment/', process_payment, name='process_payment'),
]