from django.contrib import admin
from core.models import User, AudioFile, TokenPurchase, UserAction, UserStripeRecord

# Register your models here.
admin.site.register(User)
admin.site.register(AudioFile)
admin.site.register(TokenPurchase)
admin.site.register(UserAction)
admin.site.register(UserStripeRecord)