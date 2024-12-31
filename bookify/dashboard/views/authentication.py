from dashboard.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import auth, messages
from datetime import datetime




def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Please provide both username and password')
            return redirect('dashboard-login')

        user = auth.authenticate(request, username=username, password=password)


        if user is None:
            messages.error(request, 'Invalid username or password!')
        elif user.is_active:
            if user.user_type == 1:
                auth.login(request, user)
                request.session['username'] = username
                messages.success(request, 'Admin Logged in!')
                return redirect('dashboard-home')
            else:
                messages.error(request, "Access Denied! Only admin users can log in.")
        else:
            messages.error(request, "Your account is inactive. Please contact the administrator.")
        return redirect('dashboard-login')
    return render(request, "dashboard/webpages/login.html")

@login_required
def home(request):
    if request.user.user_type != 1:
        messages.error(request, "Access Denied!")
        return redirect("dashboard-login")
    else:
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        context = {
            'user': request.user,
            'greeting': greeting,
            'is_superuser': request.user.is_superuser
        }
        return render(request, "dashboard/webpages/index.html", context)
