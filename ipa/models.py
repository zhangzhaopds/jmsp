from django.db import models

# Create your models here.

class UserInfo(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    is_active = models.BooleanField(default=0)
    def __str__(self):
        return self.user_name