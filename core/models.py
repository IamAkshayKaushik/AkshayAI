# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.conf import settings

# class User(AbstractUser):
#     phone_number = models.CharField(max_length=20, null=True, unique=True)
#     tokens = models.IntegerField(default=100)
#     is_verified = models.BooleanField(default=False)

#     def __str__(self):
#         return self.username

# class Subscription(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     active = models.BooleanField(default=False)
#     subscription_ends = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.user}'s subscription"

# class TokenTransaction(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=8, decimal_places=2)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user}'s token transaction"

# class UserAction(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     action = models.CharField(max_length=255)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user}'s action: {self.action}"

# class Subscription(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=False)

# class Payment(models.Model):
#     subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField()
#     amount = models.DecimalField(max_digits=8, decimal_places=2)




from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.utils.translation import ugettext_lazy as _
from django.conf import settings
# import timezone from django
from django.utils import timezone
from datetime import datetime, timedelta
import os



def now_plus_30():
    return timezone.now() + timedelta(days=30)


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, null=True, unique=True)
    tokens = models.PositiveIntegerField(default=100)
    is_verified = models.BooleanField(default=False)

class TokenPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    tokens = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s token purchase"

class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s action: {self.action}"

class UserStripeRecord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(default=now_plus_30)

    def is_active(self):
        return self.active and self.end_date >= timezone.now()

class AudioFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    audio_url = models.FileField(upload_to='audio/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    audio_id = models.CharField(max_length=255)

    def delete(self, using=None, keep_parents=False):
        os.unlink(self.audio_url.path)
        super().delete()

    def __str__(self):
        return self.audio_id