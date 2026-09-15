from django.db import models
from django.conf import settings


class StudentInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_info')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    xp = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name()} | Balance: {self.balance} | XP: {self.xp}"


class TeacherInfo(models.Model):
    SUBJECT_CHOICES = (
        ('physics', 'Physics'),
        ('math', 'Mathematics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('cs', 'Computer Science'),
        ('english', 'English'),
        ('history', 'History'),
        ('other', 'Other'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_info')
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='other')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name()} | Subject: {self.get_subject_display()}"
