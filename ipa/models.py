from django.db import models

# Create your models here.

class User(models.Model):
    user_name = models.CharField(max_length=100)
    user_psw = models.CharField(max_length=100)
    user_email = models.EmailField()
    def __str__(self):
        return self.user_name