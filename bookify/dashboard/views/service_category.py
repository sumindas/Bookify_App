from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.forms.service_category import ServiceCategoryForm
from dashboard.models import ServiceCategory
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string

@login_required
def service_category_manager(request):
    search_query = request.GET.get('search', '')
    categories = ServiceCategory.objects.filter(is_deleted=False)
    
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    categories = categories.order_by('-id')
    
    form = ServiceCategoryForm()
    context = {
        'categories': categories,
        'title': 'Service Categories',
        'form': form,
        'search_query': search_query
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
        form = ServiceCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service category added successfully!')
            return redirect('dashboard-service-category-manager')
        else:
            for field, errors in form.errors.items():
                e = 'Field: {} Errors: {}'.format(field, ','.join(errors))
                messages.error(request, e)
            return redirect('dashboard-service-category-manager')
    else:
        form = ServiceCategoryForm()
        context = {
            'form': form,
            'category': category
        }
        return render(request, 'dashboard/includes/modals/update_in_modal.html', context)

@login_required
def service_category_edit(request, pk):
    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service category updated successfully!')
            return redirect('dashboard-service-category-manager')
        else:
            for field, errors in form.errors.items():
                e = 'Field: {} Errors: {}'.format(field, ','.join(errors))
                messages.error(request, e)
            return redirect('dashboard-service-category-manager')
    else:
        form = ServiceCategoryForm(instance=category)
        context = {
            'form': form,
            'category': category
        }
        return render(request, 'dashboard/includes/modals/update_in_modal.html', context)

@login_required
def service_category_delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(ServiceCategory, pk=pk)
        category.is_deleted = True
        category.save()
        messages.success(request, 'Service category deleted successfully!')
        return redirect('dashboard-service-category-manager')
    return redirect('dashboard-service-category-manager')