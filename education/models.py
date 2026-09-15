from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=200)
    duration = models.PositiveIntegerField(help_text='Duration in months')
    description = models.TextField(blank=True)
    lesson_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price for one lesson')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_groups')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    level = models.PositiveIntegerField(default=1, help_text='Month number')
    teacher_share = models.DecimalField(max_digits=4, decimal_places=2, default=0.30, help_text='Part of payment to teacher (e.g. 0.30)')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='student_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Level {self.level})"

    def teacher_share_percent(self):
        return int(self.teacher_share * 100)


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons')
    context = models.TextField(blank=True, help_text='Text info')
    video = models.URLField(blank=True, help_text='YouTube link')
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.group.name}"


class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    is_absent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lesson', 'student')

    def __str__(self):
        status = "Absent" if self.is_absent else "Present"
        return f"{self.student.get_full_name()} - {self.lesson.title} ({status})"


class Homework(models.Model):
    task = models.TextField(help_text='Task description')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='homeworks')
    file = models.FileField(upload_to='homework_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"HW for {self.lesson.title}"


class Submission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    context = models.TextField(blank=True, help_text='Text context')
    file = models.FileField(upload_to='submission_files/', blank=True, null=True)
    points = models.PositiveIntegerField(default=0, help_text='Points from 0 to 100')
    is_graded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('homework', 'student')

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.homework}"

    def earned_xp(self):
        if self.is_graded:
            return int(self.points / 100 * 10)
        return 0
