from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from dashboard.models import *
from django.contrib.gis.geos import Point
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied

@login_required
def manage_shops(request):
    context = {
        'title': 'Manage Shops'
    }
    return render(request, 'dashboard/webpages/manage_shops.html', context)
    

@login_required
def shop_details(request, pk):
    """
    View function for displaying service provider details
    """
    provider = get_object_or_404(ServiceProvider, pk=pk)
    
    # Check if user has permission to view this provider
    
    # Get related services and shop slots
    services = Service.objects.filter(provider=provider, is_deleted=False)
    shop_slots = ShopSlot.objects.filter(provider=provider, is_deleted=False).first()
    
    context = {
        'provider': provider,
        'services': services,
        'shop_slots': shop_slots,
        'page_title': f'{provider.shop_name} - Details'
    }
    
    return render(request, 'dashboard/webpages/space_view.html', context)

@login_required
def update_provider(request, pk):
    """
    View function for updating service provider details
    Handles both GET (form display) and POST (form submission)
    """
    provider = get_object_or_404(ServiceProvider, pk=pk)
    
    # Check if user has permission to update this provider
    if not (request.user.is_staff or request.user == provider.user):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            provider = form.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Service provider updated successfully.'
                })
            
            messages.success(request, 'Service provider updated successfully.')
            return redirect('provider_detail', pk=provider.pk)
    else:
        form = ServiceProviderForm(instance=provider)
    
    context = {
        'form': form,
        'provider': provider,
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            template_name="dashboard/includes/forms/provider_form.html",
            context=context
        )
        return HttpResponse(html)
    
    return render(request, "dashboard/update_provider.html", context)

@login_required
def delete_provider(request, pk):
    """
    View function for soft deleting a service provider
    """
    if request.method == 'POST':
        provider = get_object_or_404(ServiceProvider, pk=pk)
        
        # Check if user has permission to delete this provider
        if not (request.user.is_staff or request.user == provider.user):
            raise PermissionDenied
        
        # Soft delete
        provider.is_deleted = True
        provider.save()
        
        # Also soft delete related services and slots
        Service.objects.filter(provider=provider).update(is_deleted=True)
        ShopSlot.objects.filter(provider=provider).update(is_deleted=True)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Service provider deleted successfully.'
            })
        
        messages.success(request, 'Service provider deleted successfully.')
        return redirect('provider_list')  # Redirect to provider list page
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })

@login_required
def toggle_provider_verification(request, pk):
    """
    View function for toggling provider verification status
    Only available to staff users
    """
    if not request.user.is_staff:
        raise PermissionDenied
        
    if request.method == 'POST':
        provider = get_object_or_404(ServiceProvider, pk=pk)
        provider.is_verified = not provider.is_verified
        provider.save()
        
        return JsonResponse({
            'status': 'success',
            'verified': provider.is_verified,
            'message': f'Provider {"verified" if provider.is_verified else "unverified"} successfully.'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })

# Additional helper functions

def update_onboarding_progress(provider):
    """
    Helper function to calculate and update onboarding progress
    """
    progress = 0
    total_steps = 6  # Adjust based on your onboarding requirements
    
    # Calculate progress based on completed steps
    if provider.shop_name:
        progress += 1
    if provider.category:
        progress += 1
    if provider.address and provider.location:
        progress += 1
    if provider.opening_time and provider.closing_time:
        progress += 1
    if provider.verification_documents:
        progress += 1
    if Service.objects.filter(provider=provider, is_deleted=False).exists():
        progress += 1
    
    # Update progress percentage
    provider.onboarding_progress = int((progress / total_steps) * 100)
    provider.is_onboarding_complete = provider.onboarding_progress == 100
    provider.save()


@login_required
def shop_list(request):
    if request.user.user_type == 1:
        draw = request.GET.get('draw')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_dir = request.GET.get("order[0][dir]", "desc")

        # Initial queryset
        shops_queryset   = ServiceProvider.objects.filter(is_deleted=False)

        # Search
        if search_value:
            shops_queryset = shops_queryset.filter(
                Q(shop_name__icontains=search_value) |
                Q(category__name__icontains=search_value)
            )

        total_records = shops_queryset.count()

        if order_dir == "desc":
            shops_queryset = shops_queryset.order_by("id")
        else:
            shops_queryset = shops_queryset.order_by("-id")


        # Pagination
        shops = shops_queryset[start:start + length]

        data = [{
            'id': shop.id,
            'name': shop.shop_name,
            'category': shop.category.name if shop.category else '',
            'type': shop.shop_type,
            'address': shop.address,
            'opening_time': shop.opening_time,
            'closing_time': shop.closing_time,
            'team_size': shop.team_size,
            'booking_preferences': shop.booking_preferences,
            'created': shop.created_at.strftime('%d %b %Y'),
            'owner': f"{shop.user.name}",
        } for shop in shops]

        response = {
            'draw': int(draw) if draw is not None else 0,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data,
        }

        return JsonResponse(response)
    else:
        return JsonResponse({'error': 'Access Denied'}, status=403)

@login_required
def edit_shop(request, shop_id):
    shop = get_object_or_404(ServiceProvider, id=shop_id)
    categories = ServiceCategory.objects.all()
    
    if request.method == 'POST':
        shop.shop_name = request.POST.get('shop_name')
        shop.category_id = request.POST.get('category')
        shop.shop_type = request.POST.get('shop_type')
        shop.address = request.POST.get('address')
        
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude and longitude:
            shop.location = Point(float(longitude), float(latitude))
        
        shop.opening_time = request.POST.get('opening_time')
        shop.closing_time = request.POST.get('closing_time')
        shop.team_size = request.POST.get('team_size')
        shop.booking_preferences = request.POST.get('booking_preferences')
        
        shop.save()
        messages.success(request, f"Shop '{shop.shop_name}' has been updated successfully.")
        return redirect('manage_shops')
    
    context = {
        'shop': shop,
        'categories': categories,
    }
    return render(request, 'dashboard/webpages/edit_shop.html', context)


