from django.contrib import admin
from .models import StudentInfo, TeacherInfo


@admin.register(StudentInfo)
class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'xp')


@admin.register(TeacherInfo)
class TeacherInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'balance')
