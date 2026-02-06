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
# Dashboard (Protected)
# --------------------
@login_required
def dashboard(request):
    if request.method == 'POST':

        task_id = request.POST.get('task_id')

        # Delete task
        if 'delete' in request.POST and task_id:
            Task.objects.filter(
                id=task_id,
                user=request.user
            ).delete()
            return redirect('dashboard')

        # Toggle task
        if task_id:
            task = Task.objects.get(
                id=task_id,
                user=request.user
            )
            task.is_completed = not task.is_completed
            task.save()
            return redirect('dashboard')

        # Create new task
        title = request.POST.get('title')
        if title:
            Task.objects.create(
                title=title,
                user=request.user
            )
            return redirect('dashboard')

    tasks = Task.objects.filter(user=request.user)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()

    progress_percent = 0
    if total_tasks > 0:
        progress_percent = int((completed_tasks / total_tasks) * 100)

    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress_percent': progress_percent,
    }

    return render(request, 'dashboard.html', context)




    


# --------------------
# URL Patterns
# --------------------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),

    # Auth
    path('accounts/signup/', signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]
