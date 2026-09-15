from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from authentication.models import CustomUser
from accounts.models import StudentInfo, TeacherInfo
from .models import Course, Group, Lesson, Attendance, Homework, Submission
from .forms import LessonForm, HomeworkForm, SubmissionForm, GradeSubmissionForm


def teacher_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_teacher():
            messages.error(request, 'Only teachers can access this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return wrapper


# ---------- TEACHER DASHBOARD ----------

@teacher_required
def teacher_dashboard(request):
    teacher = request.user
    groups = teacher.teaching_groups.all()
    lessons = Lesson.objects.filter(group__in=groups)
    pending_submissions = Submission.objects.filter(
        homework__lesson__group__in=groups, is_graded=False
    ).select_related('student', 'homework')

    context = {
        'groups': groups,
        'lessons': lessons,
        'pending_submissions': pending_submissions,
    }
    return render(request, 'education/teacher_dashboard.html', context)


# ---------- COURSES (public listing) ----------

@login_required
def course_list(request):
    courses = Course.objects.all().prefetch_related('groups')
    return render(request, 'education/course_list.html', {'courses': courses})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    groups = course.groups.all()
    if request.user.is_teacher():
        groups = groups.filter(teacher=request.user)
    elif request.user.is_student():
        groups = groups.filter(students=request.user)
    return render(request, 'education/course_detail.html', {'course': course, 'groups': groups})


# ---------- LESSONS ----------

@teacher_required
def lesson_create(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    if group.teacher != request.user:
        messages.error(request, 'This group is not assigned to you.')
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.group = group
            lesson.save()
            messages.success(request, f'Lesson "{lesson.title}" created.')
            return redirect('group_detail', pk=group.pk)
    else:
        form = LessonForm()
    return render(request, 'education/lesson_form.html', {'form': form, 'group': group, 'title': 'Create Lesson'})


@teacher_required
def lesson_edit(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if lesson.group.teacher != request.user:
        messages.error(request, 'You can only edit your own lessons.')
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated.')
            return redirect('lesson_detail', pk=lesson.pk)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'education/lesson_form.html', {'form': form, 'group': lesson.group, 'title': 'Edit Lesson'})


@teacher_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if lesson.group.teacher != request.user:
        messages.error(request, 'You can only delete your own lessons.')
        return redirect('teacher_dashboard')
    group_pk = lesson.group.pk
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted.')
        return redirect('group_detail', pk=group_pk)
    return render(request, 'education/confirm_delete.html', {'object': lesson})


def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    group = lesson.group
    allowed = (
        request.user.is_manager()
        or (request.user.is_teacher() and request.user == group.teacher)
        or request.user.student_groups.filter(pk=group.pk).exists()
    )
    if not allowed:
        messages.error(request, 'You do not have access to this lesson.')
        return redirect('dashboard')

    homeworks = lesson.homeworks.all()
    context = {
        'lesson': lesson,
        'group': group,
        'homeworks': homeworks,
    }
    return render(request, 'education/lesson_detail.html', context)


# ---------- HOMEWORK ----------

@teacher_required
def homework_create(request, lesson_pk):
    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    if lesson.group.teacher != request.user:
        messages.error(request, 'You can only add homework to your groups.')
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.lesson = lesson
            homework.save()
            messages.success(request, 'Homework created.')
            return redirect('lesson_detail', pk=lesson.pk)
    else:
        form = HomeworkForm()
    return render(request, 'education/homework_form.html', {'form': form, 'lesson': lesson, 'title': 'Create Homework'})


@teacher_required
def homework_edit(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    if homework.lesson.group.teacher != request.user:
        messages.error(request, 'You can only edit your own homework.')
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES, instance=homework)
        if form.is_valid():
            form.save()
            messages.success(request, 'Homework updated.')
            return redirect('homework_detail', pk=homework.pk)
    else:
        form = HomeworkForm(instance=homework)
    return render(request, 'education/homework_form.html', {'form': form, 'lesson': homework.lesson, 'title': 'Edit Homework'})


def homework_detail(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    lesson = homework.lesson
    group = lesson.group
    allowed = (
        request.user.is_manager()
        or (request.user.is_teacher() and request.user == group.teacher)
        or request.user.student_groups.filter(pk=group.pk).exists()
    )
    if not allowed:
        messages.error(request, 'You do not have access to this homework.')
        return redirect('dashboard')

    is_teacher = request.user.is_teacher()
    is_student = request.user.student_groups.filter(pk=group.pk).exists()

    submissions = homework.submissions.all()
    my_submission = None
    if is_student:
        my_submission = submissions.filter(student=request.user).first()

    context = {
        'homework': homework,
        'lesson': lesson,
        'group': group,
        'submissions': submissions,
        'my_submission': my_submission,
        'is_teacher': is_teacher,
        'is_student': is_student,
    }
    return render(request, 'education/homework_detail.html', context)


# ---------- SUBMISSION (by student) ----------

@login_required
def submission_create(request, homework_pk):
    homework = get_object_or_404(Homework, pk=homework_pk)
    group = homework.lesson.group
    if not request.user.student_groups.filter(pk=group.pk).exists():
        messages.error(request, 'You are not in this group.')
        return redirect('dashboard')

    existing = Submission.objects.filter(homework=homework, student=request.user).first()
    if existing:
        messages.info(request, 'You already submitted this homework.')
        return redirect('homework_detail', pk=homework.pk)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.homework = homework
            submission.student = request.user
            submission.save()
            messages.success(request, 'Homework submitted successfully.')
            return redirect('homework_detail', pk=homework.pk)
    else:
        form = SubmissionForm()
    return render(request, 'education/submission_form.html', {'form': form, 'homework': homework})


# ---------- GRADE SUBMISSION (by teacher) ----------

@teacher_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    homework = submission.homework
    if homework.lesson.group.teacher != request.user:
        messages.error(request, 'You cannot grade submission from other group.')
        return redirect('teacher_dashboard')

    was_graded = submission.is_graded
    old_points = submission.points

    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.is_graded = True
            submission.save()

            # give XP: points / 100 * 10 (integer)
            student_info = submission.student.student_info
            if not was_graded:
                # first time grading -> add XP
                xp = submission.earned_xp()
                student_info.xp += xp
                student_info.save()
                messages.success(request, f'Submission graded. Student earned {xp} XP.')
            else:
                # re-grade -> update XP with the difference
                old_xp = int(old_points / 100 * 10)
                new_xp = submission.earned_xp()
                student_info.xp += (new_xp - old_xp)
                student_info.save()
                messages.success(request, 'Submission re-graded.')
            return redirect('homework_detail', pk=homework.pk)
    else:
        form = GradeSubmissionForm(instance=submission)
    return render(request, 'education/grade_submission.html', {'form': form, 'submission': submission})


# ---------- ATTENDANCE ----------

@teacher_required
def attendance_view(request, lesson_pk):
    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    group = lesson.group
    if group.teacher != request.user:
        messages.error(request, 'You can only mark attendance for your groups.')
        return redirect('teacher_dashboard')

    students = group.students.all()

    if request.method == 'POST':
        absent_ids = request.POST.getlist('absent')
        for student in students:
            attendance, created = Attendance.objects.get_or_create(
                lesson=lesson, student=student, defaults={'is_absent': False}
            )
            is_absent = str(student.pk) in absent_ids
            attendance.is_absent = is_absent
            attendance.save()

            # money logic: student present -> charge student, pay teacher
            if not is_absent:
                student_info, _ = StudentInfo.objects.get_or_create(user=student)
                teacher_info, _ = TeacherInfo.objects.get_or_create(user=group.teacher)
                price = group.course.lesson_price
                teacher_amount = price * group.teacher_share
                if student_info.balance >= price:
                    student_info.balance -= price
                    student_info.save()
                    teacher_info.balance += teacher_amount
                    teacher_info.save()
                else:
                    messages.warning(request, f'{student.get_full_name()} has not enough balance for this lesson.')
        messages.success(request, 'Attendance saved.')
        return redirect('lesson_detail', pk=lesson_pk)

    attendances = {
        a.student.pk: a for a in Attendance.objects.filter(lesson=lesson)
    }
    share_amount = group.course.lesson_price * group.teacher_share
    context = {
        'lesson': lesson,
        'group': group,
        'students': students,
        'attendances': attendances,
        'share_amount': share_amount,
    }
    return render(request, 'education/attendance.html', context)


# ---------- LEADERBOARD ----------

@login_required
def leaderboard(request):
    group_filter = request.GET.get('group', 'all')

    students = CustomUser.objects.filter(role='student')
    all_groups = Group.objects.all()

    if group_filter != 'all':
        all_groups = all_groups.filter(pk=group_filter)
        group = all_groups.first()
        if group:
            students = group.students.all()

    leaderboard_list = []
    for student in students:
        info, _ = StudentInfo.objects.get_or_create(user=student)
        leaderboard_list.append({
            'student': student,
            'xp': info.xp,
        })

    leaderboard_list.sort(key=lambda x: x['xp'], reverse=True)

    context = {
        'leaderboard_list': leaderboard_list,
        'all_groups': Group.objects.all(),
        'current_filter': group_filter,
    }
    return render(request, 'education/leaderboard.html', context)