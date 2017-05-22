from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    avatar = models.URLField(null=True)
    def __str__(self):
        return self.user.email
