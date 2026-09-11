from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class UserRoles(models.TextChoices):
        STUDENT = 'STUDENT', 'student'
        TEACHER = 'TEACHER', 'teacher'
        MANAGER = 'MANAGER', 'manager'
        
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    user_role = models.CharField(max_length=15, choices=UserRoles.choices)
    
    
    