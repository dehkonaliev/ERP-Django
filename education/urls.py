from django.urls import path
from . import views

urlpatterns = [
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('groups/<int:group_pk>/lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/edit/', views.lesson_edit, name='lesson_edit'),
    path('lessons/<int:pk>/delete/', views.lesson_delete, name='lesson_delete'),
    path('lessons/<int:lesson_pk>/attendance/', views.attendance_view, name='attendance_view'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_pk>/homeworks/create/', views.homework_create, name='homework_create'),
    path('homeworks/<int:pk>/edit/', views.homework_edit, name='homework_edit'),
    path('homeworks/<int:homework_pk>/submit/', views.submission_create, name='submission_create'),
    path('homeworks/<int:pk>/', views.homework_detail, name='homework_detail'),
    path('submissions/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]