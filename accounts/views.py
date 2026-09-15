from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from authentication.models import CustomUser
from authentication.forms import CustomUserCreationForm
from accounts.models import StudentInfo, TeacherInfo
from education.models import Group, Course, Lesson
from finance.models import Payment
from .forms import GroupForm, ReplenishBalanceForm, CourseForm, StudentGroupsForm


def manager_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_manager():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return wrapper


# ---------- DASHBOARD ----------

@manager_required
def manager_dashboard(request):
    total_students = CustomUser.objects.filter(role='student').count()
    total_teachers = CustomUser.objects.filter(role='teacher').count()
    total_groups = Group.objects.count()
    total_courses = Course.objects.count()
    recent_payments = Payment.objects.all()[:10]
    recent_groups = Group.objects.all()[:10]

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_groups': total_groups,
        'total_courses': total_courses,
        'recent_payments': recent_payments,
        'recent_groups': recent_groups,
    }
    return render(request, 'accounts/manager_dashboard.html', context)


# ---------- USERS ----------

@manager_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'student':
                StudentInfo.objects.create(user=user)
            elif user.role == 'teacher':
                subject = request.POST.get('subject', 'other')
                TeacherInfo.objects.create(user=user, subject=subject)
            messages.success(request, f'User "{user.get_full_name()}" created successfully.')
            return redirect('student_list' if user.role == 'student' else 'teacher_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/user_form.html', {'form': form})


@manager_required
def student_list(request):
    students = CustomUser.objects.filter(role='student')
    context = {
        'students': students,
        'title': 'Students',
    }
    return render(request, 'accounts/user_list.html', context)


@manager_required
def teacher_list(request):
    teachers = CustomUser.objects.filter(role='teacher')
    context = {
        'teachers': teachers,
        'title': 'Teachers',
    }
    return render(request, 'accounts/teacher_list.html', context)


def student_dashboard(request):
    student = request.user
    if not student.is_student():
        messages.error(request, 'Only students can access this page.')
        return redirect('dashboard')
    groups = student.student_groups.all().select_related('course', 'teacher')
    return render(request, 'accounts/student_dashboard.html', {'groups': groups})


def student_detail(request, pk):
    profile_user = get_object_or_404(CustomUser, pk=pk, role='student')
    is_manager = request.user.is_manager()
    is_self = request.user == profile_user
    if not (is_manager or is_self):
        messages.error(request, 'You can only view your own profile.')
        return redirect('dashboard')

    try:
        student_info = profile_user.student_info
    except StudentInfo.DoesNotExist:
        student_info = StudentInfo.objects.create(user=profile_user)

    groups = profile_user.student_groups.all()
    payments = Payment.objects.filter(student=profile_user)
    submissions = profile_user.submissions.all()

    context = {
        'profile_user': profile_user,
        'student_info': student_info,
        'groups': groups,
        'payments': payments,
        'submissions': submissions,
    }
    return render(request, 'accounts/student_detail.html', context)


def teacher_detail(request, pk):
    profile_user = get_object_or_404(CustomUser, pk=pk, role='teacher')
    is_manager = request.user.is_manager()
    is_self = request.user == profile_user
    if not (is_manager or is_self):
        messages.error(request, 'You can only view your own profile.')
        return redirect('dashboard')

    try:
        teacher_info = profile_user.teacher_info
    except TeacherInfo.DoesNotExist:
        teacher_info = TeacherInfo.objects.create(user=profile_user)

    groups = profile_user.teaching_groups.all()
    lesson_count = Lesson.objects.filter(group__in=groups).count()
    shares = set(g.teacher_share_percent() for g in groups)

    context = {
        'profile_user': profile_user,
        'teacher_info': teacher_info,
        'groups': groups,
        'lesson_count': lesson_count,
        'shares': sorted(shares, reverse=True),
    }
    return render(request, 'accounts/teacher_detail.html', context)


# ---------- GROUPS ----------

@manager_required
def group_list(request):
    groups = Group.objects.all().prefetch_related('course', 'teacher', 'students')
    return render(request, 'accounts/group_list.html', {'groups': groups})


@manager_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.students.set(form.cleaned_data.get('students'))
            messages.success(request, f'Group "{group.name}" created.')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'accounts/group_form.html', {'form': form, 'title': 'Create Group'})


@manager_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            group.students.set(form.cleaned_data.get('students'))
            messages.success(request, f'Group "{group.name}" updated.')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm(instance=group)
    return render(request, 'accounts/group_form.html', {'form': form, 'title': 'Edit Group'})


@manager_required
def student_add_to_group(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    if request.method == 'POST':
        form = StudentGroupsForm(request.POST)
        if form.is_valid():
            student.student_groups.set(form.cleaned_data['groups'])
            messages.success(request, f'Groups of {student.get_full_name()} updated.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentGroupsForm(initial={'groups': student.student_groups.all()})
    return render(request, 'accounts/student_add_to_group.html', {'form': form, 'student': student})


def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    allowed = (
        request.user.is_manager()
        or (request.user.is_teacher() and request.user == group.teacher)
        or request.user.student_groups.filter(pk=group.pk).exists()
    )
    if not allowed:
        messages.error(request, 'You do not have access to this group.')
        return redirect('dashboard')

    lessons = group.lessons.all()
    students = group.students.all()
    context = {
        'group': group,
        'lessons': lessons,
        'students': students,
    }
    return render(request, 'education/group_detail.html', context)


# ---------- COURSE ----------

@manager_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created.')
            return redirect('manager_dashboard')
    else:
        form = CourseForm()
    return render(request, 'accounts/course_form.html', {'form': form})


# ---------- FINANCE ----------

@manager_required
def replenish_balance(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    student_info = get_object_or_404(StudentInfo, user=student)
    if request.method == 'POST':
        form = ReplenishBalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            student_info.balance += amount
            student_info.save()
            Payment.objects.create(
                student=student,
                amount=amount,
                description='Balance replenishment by manager',
            )
            messages.success(request, f'Balance of {student.get_full_name()} topped up by ${amount}.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = ReplenishBalanceForm()
    return render(request, 'accounts/replenish_balance.html', {'form': form, 'student': student, 'student_info': student_info})