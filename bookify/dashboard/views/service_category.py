
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.forms.service_category import ServiceCategoryForm
from dashboard.models import ServiceCategory
from django.http import JsonResponse
from django.db.models import Q

@login_required
def service_category_manager(request):
    categories = ServiceCategory.objects.all()
    context = {
        'categories': categories,
        'title': 'Service Categories'
    }
    return render(request, 'dashboard/webpages/service_category.html', context)

@login_required
def service_category_list(request):
    if request.user.user_type == 1:
        draw = request.GET.get('draw')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_dir = request.GET.get("order[0][dir]", "desc")

        # Initial queryset
        categories_queryset = ServiceCategory.objects.filter(is_deleted=False)

        # Search
        if search_value:
            categories_queryset = categories_queryset.filter(
                Q(name__icontains=search_value) |
                Q(description__icontains=search_value)
            )

        total_records = categories_queryset.count()

        if order_dir == "desc":
            categories_queryset = categories_queryset.order_by("id")
        else:
            categories_queryset = categories_queryset.order_by("-id")

        # Pagination
        categories = categories_queryset[start:start + length]

        data = [{
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'created': category.created_at.strftime('%Y-%m-%d %H:%M:%S') if category.created_at else '',
        } for category in categories]

        response = {
            'draw': int(draw),
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data,
        }

        return JsonResponse(response)
    else:
        return JsonResponse({'error': 'Access Denied'}, status=403)


@login_required
def service_category_add(request):
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service category added successfully!')
            return redirect('dashboard:service_category_list')
    else:
        form = ServiceCategoryForm()
    
    context = {
        'form': form,
        'title': 'Add Service Category'
    }
    return render(request, 'dashboard/service_category/form.html', context)

@login_required
def service_category_edit(request, pk):
    category = ServiceCategory.objects.get(pk=pk)
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service category updated successfully!')
            return redirect('dashboard:service_category_list')
    else:
        form = ServiceCategoryForm(instance=category)
    
    context = {
        'form': form,
        'title': 'Edit Service Category'
    }
    return render(request, 'dashboard/service_category/form.html', context)
