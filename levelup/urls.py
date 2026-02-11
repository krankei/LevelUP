from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from datetime import date, timedelta

from tasks.models import Task, WeeklyProgress, UserProfile


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)  # create profile
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    mode = request.GET.get('mode', 'daily')

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        action = request.POST.get('action')
        selected_date = request.POST.get('selected_date')

        if 'delete' in request.POST and task_id:
            Task.objects.filter(id=task_id, user=request.user).delete()
            return redirect('dashboard')

        # WEEKLY toggle with XP
        if action == 'toggle_weekly' and task_id and selected_date:
            task = Task.objects.get(id=task_id, user=request.user)
            progress, _ = WeeklyProgress.objects.get_or_create(
                task=task,
                date=selected_date
            )

            progress.is_completed = not progress.is_completed
            progress.save()

            if progress.is_completed:
                profile.total_xp += task.xp_value
            else:
                profile.total_xp -= task.xp_value

            profile.calculate_level()
            return redirect('dashboard')

        # DAILY toggle with XP
        if action == 'toggle_today' and task_id:
            task = Task.objects.get(id=task_id, user=request.user)
            progress, _ = WeeklyProgress.objects.get_or_create(
                task=task,
                date=today
            )

            progress.is_completed = not progress.is_completed
            progress.save()

            if progress.is_completed:
                profile.total_xp += task.xp_value
            else:
                profile.total_xp -= task.xp_value

            profile.calculate_level()
            return redirect('dashboard')

        # Create task
        if mode == 'daily':
            title = request.POST.get('title')
            task_type = request.POST.get('task_type')
            time_slot = request.POST.get('time_slot')
            duration = request.POST.get('duration_hours')

            if title and task_type:
                if task_type == "MAIN" and not time_slot:
                    return redirect('dashboard')

                Task.objects.create(
                    title=title,
                    user=request.user,
                    task_type=task_type,
                    time_slot=time_slot if task_type == "MAIN" else None,
                    duration_hours=int(duration) if duration else 1
                )
                return redirect('dashboard')

    main_tasks = Task.objects.filter(
        user=request.user,
        task_type='MAIN'
    ).order_by('time_slot')

    side_tasks = Task.objects.filter(
        user=request.user,
        task_type='SIDE'
    )

    weekly_tasks = main_tasks

    weekly_progress = {}
    for task in weekly_tasks:
        weekly_progress[task.id] = {}
        for d in week_dates:
            record = WeeklyProgress.objects.filter(task=task, date=d).first()
            weekly_progress[task.id][d] = record.is_completed if record else False

    today_progress = {}
    for task in main_tasks:
        record = WeeklyProgress.objects.filter(task=task, date=today).first()
        today_progress[task.id] = record.is_completed if record else False

    total_today = len(main_tasks)
    completed_today = sum(today_progress.values())
    progress_percent = int((completed_today / total_today) * 100) if total_today else 0

    total_week_tasks = len(main_tasks) * 7
    completed_week = 0
    for task in main_tasks:
        for d in week_dates:
            record = WeeklyProgress.objects.filter(task=task, date=d).first()
            if record and record.is_completed:
                completed_week += 1

    weekly_percent = int((completed_week / total_week_tasks) * 100) if total_week_tasks else 0

    streak = 0
    check_day = today

    while True:
        all_completed = True

        for task in main_tasks:
            record = WeeklyProgress.objects.filter(task=task, date=check_day).first()
            if not record or not record.is_completed:
                all_completed = False
                break

        if all_completed and main_tasks.exists():
            streak += 1
            check_day -= timedelta(days=1)
        else:
            break
    # 🔥 XP Progress Bar Logic
    next_level_xp = 500 + (profile.level - 1) * 250
    current_level_start_xp = 500 + (profile.level - 2) * 250 if profile.level > 1 else 0

    xp_progress = profile.total_xp - current_level_start_xp
    xp_needed = next_level_xp - current_level_start_xp

    xp_percent = int((xp_progress / xp_needed) * 100) if xp_needed > 0 else 0

    return render(request, 'dashboard.html', {
        'main_tasks': main_tasks,
        'side_tasks': side_tasks,
        'weekly_tasks': weekly_tasks,
        'week_dates': week_dates,
        'weekly_progress': weekly_progress,
        'today_progress': today_progress,
        'progress_percent': progress_percent,
        'weekly_percent': weekly_percent,
        'streak': streak,
        'mode': mode,
        'today': today,
        'total_xp': profile.total_xp,
        'level': profile.level,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('accounts/signup/', signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]
