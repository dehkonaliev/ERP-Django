from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import StudentInfo
from education.models import Group
from finance.models import Payment
from authentication.models import CustomUser


@login_required
def payments_list(request):
    if not request.user.is_manager():
        return render(request, 'finance/payments.html', {'payments': []})

    payments = Payment.objects.all().select_related('student')
    context = {
        'payments': payments,
        'students': CustomUser.objects.filter(role='student'),
    }
    return render(request, 'finance/payments.html', context)