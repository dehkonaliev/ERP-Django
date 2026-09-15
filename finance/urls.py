from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.payments_list, name='payments_list'),
]