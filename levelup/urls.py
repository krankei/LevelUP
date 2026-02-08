from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from tasks.models import Task


# --------------------
# Home Page
# --------------------
def home(request):
    return render(request, 'home.html')


# --------------------
# Signup Page
# --------------------
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


# --------------------
# Dashboard
# --------------------
@login_required
def dashboard(request):
    mode = request.GET.get('mode', 'daily')

    if request.method == 'POST':
        task_id = request.POST.get('task_id')

        # ❌ Delete task
        if 'delete' in request.POST and task_id:
            Task.objects.filter(
                id=task_id,
                user=request.user
            ).delete()
            return redirect('dashboard')

        # ✅ Toggle DAILY task only
        if task_id and mode == 'daily':
            task = Task.objects.get(
                id=task_id,
                user=request.user
            )
            task.is_completed = not task.is_completed
            task.save()
            return redirect('dashboard')

        # ➕ Create DAILY task
        if mode == 'daily':
            title = request.POST.get('title')
            if title:
                Task.objects.create(
                    title=title,
                    user=request.user,
                    is_weekly=False
                )
                return redirect('dashboard')

        # ➕ Create WEEKLY task
        if mode == 'weekly':
            title = request.POST.get('title')
            time_slot = request.POST.get('time_slot')

            if title and time_slot:
                Task.objects.create(
                    title=title,
                    time_slot=time_slot,
                    user=request.user,
                    is_weekly=True
                )
                return redirect('dashboard')

    # --------------------
    # Data for templates
    # --------------------
    tasks = Task.objects.filter(
        user=request.user,
        is_weekly=False
    )

    weekly_tasks = Task.objects.filter(
        user=request.user,
        is_weekly=True
    ).order_by('time_slot')

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    progress_percent = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    return render(request, 'dashboard.html', {
        'tasks': tasks,
        'weekly_tasks': weekly_tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress_percent': progress_percent,
        'mode': mode,
    })


# --------------------
# URL Patterns
# --------------------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('accounts/signup/', signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]
