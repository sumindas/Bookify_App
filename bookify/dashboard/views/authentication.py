from dashboard.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import auth, messages
from datetime import datetime




def login(request):
    # if 'username' in request.session:
    #     return redirect('dashboard-home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.user_type == 1:
                request.session['username'] = username
                auth.login(request, user)
                messages.success(request, 'Admin Logged in!')
                return redirect('dashboard-home')
            else:
                messages.error(request, "Access Denied! Only admin users can log in.")
                return redirect('dashboard-login')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('dashboard-login')
    return render(request, "dashboard/webpages/login.html")
    
    

@login_required
def home(request):
    if request.user.user_type != 1:
        messages.error(request, "Access Denied!")
        return redirect("dashboard-login")
    else:
        current_hour = datetime.now().hour
        print(current_hour)
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
