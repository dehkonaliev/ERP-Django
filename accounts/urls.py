from django.urls import path
from . import views

urlpatterns = [
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('users/create/', views.create_user, name='create_user'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/groups/', views.student_add_to_group, name='student_add_to_group'),
    path('students/<int:pk>/replenish/', views.replenish_balance, name='replenish_balance'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('courses/create/', views.course_create, name='course_create'),
]