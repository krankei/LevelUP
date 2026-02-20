from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def dashboard(request):
    profile = request.user.userprofile

    level = profile.level
    total_xp = profile.xp
    next_level_xp = level * 100
    xp_percent = int((total_xp / next_level_xp) * 100) if next_level_xp > 0 else 0

    return render(request, "dashboard.html", {
        "level": level,
        "total_xp": total_xp,
        "next_level_xp": next_level_xp,
        "xp_percent": xp_percent,
        "streak": profile.streak,
        "mode": "daily",
    })