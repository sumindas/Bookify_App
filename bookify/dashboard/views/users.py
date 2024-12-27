from datetime import datetime, time
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import fromstr
from django.shortcuts import redirect, render, get_object_or_404
from dashboard.models import CustomUser
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
import urllib.parse



@login_required
def user_manager(request):
    if request.user.user_type == 1:
        users = CustomUser.objects.filter(user_type=2).order_by('-id')
        context = {
                "users": users,
                "title": "Manage Users | Dashboard"
        }
        return render(request, "dashboard/webpages/user_manager.html", context)
    else:
        messages.error(request, "Access Denied!")
        return redirect('dashboard-login')


@login_required
def users_list(request):
    if request.user.user_type == 1:
        draw = request.GET.get('draw')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_dir = request.GET.get("order[0][dir]", "desc")

        # Initial queryset
        users_queryset = CustomUser.objects.filter(user_type=2,is_deleted=False)

        # Search
        if search_value:
            users_queryset = users_queryset.filter(
                Q(email__icontains=search_value) |
                Q(phone__icontains=search_value)
            )

        total_records = users_queryset.count()

        if order_dir == "desc":
            users_queryset = users_queryset.order_by("id")
        else:
            users_queryset = users_queryset.order_by("-id")


        # Pagination
        users = users_queryset[start:start + length]

        data = [{
            'id': user.id,
            'name': user.name,
            'phone': user.phone,
            'created': user.created.strftime('%Y-%m-%d %H:%M:%S'),
        } for user in users]

        response = {
            'draw': int(draw),
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data,
        }

        return JsonResponse(response)
    else:
        return JsonResponse({'error': 'Access Denied'}, status=403)