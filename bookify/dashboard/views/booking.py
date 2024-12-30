from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from dashboard.models import Booking, ServiceProvider, Service, Payment
from datetime import datetime, timedelta

@login_required
def booking_manager(request):
    """View for managing all bookings"""
    bookings_queryset = Booking.objects.filter(is_deleted=False)
    print(bookings_queryset)
    context = {
        'title': 'Manage Bookings'
    }
    return render(request, 'dashboard/webpages/booking_manager.html', context)

@login_required
def booking_list(request):
    """API endpoint for DataTables to fetch booking data"""
    
    bookings_queryset = Booking.objects.filter(is_deleted=False)

    # Get DataTables parameters
    draw = request.GET.get('draw')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')

    # Search
    if search_value:
        bookings_queryset = bookings_queryset.filter(
            Q(customer__email__icontains=search_value) |
            Q(provider__shop_name__icontains=search_value) |
            Q(service__name__icontains=search_value) |
            Q(status__icontains=search_value)
        )

    # Order
    order_columns = ['id', 'customer__email', 'provider__shop_name', 'service__name', 
                    'scheduled_time', 'status', 'total_service_price']
    if order_dir == "desc":
        bookings_queryset = bookings_queryset.order_by(f"-{order_columns[order_column]}")
    else:
        bookings_queryset = bookings_queryset.order_by(order_columns[order_column])

    total_records = bookings_queryset.count()
    bookings = bookings_queryset[start:start + length]

    data = []
    for booking in bookings:
        payment = Payment.objects.filter(booking=booking).first()
        payment_status = payment.status if payment else 'No payment'
        
        data.append({
            'id': booking.id,
            'customer': booking.customer.email,
            'provider': booking.provider.shop_name,
            'service': booking.service.name,
            'scheduled_time': booking.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            'status': booking.status,
            'payment_status': payment_status,
            'total_price': float(booking.total_service_price),
            'actions': f'''
                <div class="dropdown">
                    <button class="btn btn-soft-secondary btn-sm dropdown" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="ri-more-fill align-middle"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><button class="dropdown-item" onclick="viewBooking({booking.id})"><i class="ri-eye-fill align-bottom me-2 text-muted"></i> View</button></li>
                        {'<li><button class="dropdown-item" onclick="updateStatus(' + str(booking.id) + ', \'confirmed\')"><i class="ri-check-fill align-bottom me-2 text-muted"></i> Confirm</button></li>' if booking.status == 'pending' else ''}
                        {'<li><button class="dropdown-item" onclick="updateStatus(' + str(booking.id) + ', \'cancelled\')"><i class="ri-close-fill align-bottom me-2 text-muted"></i> Cancel</button></li>' if booking.status == 'pending' else ''}
                    </ul>
                </div>
            '''
        })
    print(data)
    response = {
        'draw': int(draw),
        'recordsTotal': total_records,
        'recordsFiltered': total_records,
        'data': data,
    }

    return JsonResponse(response)

@login_required
def booking_view(request, pk):
    """View details of a specific booking"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check if user has permission to view this booking
    if request.user.user_type == 2:  # Service Provider
        provider = ServiceProvider.objects.get(user=request.user)
        if booking.provider != provider:
            messages.error(request, "You don't have permission to view this booking.")
            return redirect('dashboard-booking-manager')
    elif request.user.user_type == 3:  # Customer
        if booking.customer != request.user:
            messages.error(request, "You don't have permission to view this booking.")
            return redirect('dashboard-booking-manager')

    payment = Payment.objects.filter(booking=booking).first()
    
    context = {
        'booking': booking,
        'payment': payment,
        'title': f'Booking #{booking.id}'
    }
    return render(request, 'dashboard/webpages/booking_view.html', context)

@login_required
def update_booking_status(request, pk):
    """Update the status of a booking"""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=pk)
        new_status = request.POST.get('status')
        
        # Check permissions
        if request.user.user_type == 2:  # Service Provider
            provider = ServiceProvider.objects.get(user=request.user)
            if booking.provider != provider:
                return JsonResponse({'error': "You don't have permission to update this booking."}, status=403)
        elif request.user.user_type != 1:  # Not admin
            return JsonResponse({'error': "You don't have permission to update bookings."}, status=403)
            
        if new_status not in ['confirmed', 'cancelled']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
            
        booking.status = new_status
        booking.save()
        
        messages.success(request, f'Booking status updated to {new_status}')
        return JsonResponse({'status': 'success'})
        
    return JsonResponse({'error': 'Invalid request method'}, status=405)
