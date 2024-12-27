
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from dashboard.models import *
from .serializers import ShopSlotSerializer, ServiceProviderSerializer, ServiceSerializer
from random import randint
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
import urllib.parse






def sendTransactionalSms(phone, message):
	API_KEY = '347d4ad8-60cd-11ec-b710-0200cd936042'
	API_ENDPOINT = 'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=' + API_KEY + '&to=' + phone + '&from=OTPQIK&msg=' + urllib.parse.quote_plus(
			message)
	requests.get(url = API_ENDPOINT)


@api_view(['POST'])
def otp_auth(request):
	phone = request.data.get('phone', False)
	request_id = request.data.get('request_id', False)
	if phone and request_id:
		username = 'partner_' + phone
		try:
			user = CustomUser.objects.get(username=username, user_type=3)
			if Otp.objects.filter(request_id=request_id, requested_by=user, verified=False).exists():
				code = Otp.objects.filter(request_id=request_id, requested_by=user, verified=False)[0].code
			else:
				code = randint(1000, 9999)
				otp = Otp(requested_by=user, code=code, request_id=request_id)
				otp.save()
			
			if phone == "919876543210":
				code = 5555
			
			message = f'Your OTP to login Bookify is {code}. Please do not share this OTP. \nPowered by Cynbus'
			if phone != "919876543210":
				sendTransactionalSms(phone, message)
			
			context = {
				'status': 'success',
				'message': 'Login OTP Send!',
				'route': 'login'
			}
			return Response(context)
		except CustomUser.DoesNotExist:
			tempuser = TempUser.objects.create(full_name="", username=username, phone=phone)
			otp = Otp()
			otp.temp_user = tempuser
			otp.request_id = request_id
			
			if phone == "919876543210":
				code = 5555
			else:
				code = randint(1000, 9999)
			
			message = f'Your OTP to login Find & Park is {code}. Please do not share this OTP. \nPowered by Cynbus'
			if phone != "919876543210":
				sendTransactionalSms(phone, message)
			
			otp.code = code
			otp.save()
			context = {
				'status': 'success',
				'message': 'Signup OTP Send!',
				'route': 'signup'
			}
			return Response(context)
	else:
		response = {
			"status": "error",
			"error_code": 0,
			"message": "incomplete request"
		}
		return Response(response)


@api_view(['POST'])
def otp_login_verify(request):
	phone = request.data.get('phone', False)
	code = request.data.get('code', False)
	request_id = request.data.get('request_id', False)
	if phone and code and request_id:
		username = 'partner_' + phone
		try:
			user = CustomUser.objects.get(username=username, user_type=3)
			if Otp.objects.filter(requested_by = user, code = code, request_id = request_id, verified = False).exists():
				otp = Otp.objects.filter(requested_by = user, code = code, request_id = request_id, verified = False).first()
				otp.verified = True
				date_from = datetime.now() - timedelta(days = 1)
				otp.created__gte = date_from
				otp.save()
				user_details = {
						'id': user.id,
						'name': user.name,
						'username': user.username,
						'phone': user.phone,
				}
				refresh = RefreshToken.for_user(user)
				context = {
						'status': 'success',
						'message': 'Login successful',
						'refresh': str(refresh),
						'access': str(refresh.access_token),
						'user': user_details,
						'new_user' : False
				}
			else:
				context = {
						'status': 'error',
						'error_code': 8,
						'message': 'Otp verification failed',
				}
		except CustomUser.DoesNotExist:
			tempusers = TempUser.objects.filter(username = username).order_by('-id')
			if tempusers:
				tempuser = tempusers[0]
				if Otp.objects.filter(temp_user = tempuser, code = code, request_id = request_id, verified = False).exists():
					otp = Otp.objects.filter(temp_user = tempuser, code = code, request_id = request_id, verified = False).first()
					otp.verified = True
					date_from = datetime.now() - timedelta(days = 1)
					otp.created__gte = date_from
					otp.save()
					new_user = CustomUser.objects.create(
							name = tempuser.full_name,
							username = tempuser.username,
							phone = tempuser.phone,
							is_mobile = True,
							user_type=3
					)
					new_user.save()
					tempuser.is_deleted = True
					tempuser.save()
					user_details = {
						'id': new_user.id,
						'name': new_user.name,
						'username': new_user.username,
						'phone': new_user.phone,
					}
					refresh = RefreshToken.for_user(new_user)
					context = {
							'status': 'success',
							'message': 'OTP Verified and logged in!',
							'user': user_details,
							'refresh': str(refresh),
							'access': str(refresh.access_token),
							'new_user' : True
					}
				
				else:
					context = {
						'status': 'error',
						'error_code': 8,
						'message': 'Otp verification failed',
					}
			else:
				context = {
					'status': 'error',
					'error_code': 8,
					'message': 'Otp verification failed',
				}
		return Response(context)
	else:
		response = {
				"status": "error",
				"error_code": 0,
				"message": "incomplete request"
		}
		return Response(response)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_business_type(request):
    """Select the type of business."""
    try:
        category_id = request.data.get('category_id')
        if not category_id:
            return Response({"error": "Category ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(ServiceCategory, id=category_id)
        
        service_provider, created = ServiceProvider.objects.get_or_create(
            user=request.user,
            defaults={'category': category}
        )
        
        if not created:
            service_provider.category = category
            service_provider.save()
        
        service_provider.onboarding_progress = 1
        service_provider.save()
        
        return Response({
            "message": "Business type selected successfully",
            "category": category.name
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Step 2: Business Information
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_business_info(request):
    """Update business information."""
    try:
        service_provider = get_object_or_404(ServiceProvider, user=request.user)
        
        required_fields = ['shop_name', 'shop_type', 'address']
        if any(field not in request.data for field in required_fields):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle location data
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        if latitude and longitude:
            location = Point(float(longitude), float(latitude))
            request.data['location'] = location

        serializer = ServiceProviderSerializer(service_provider, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            service_provider.onboarding_progress = 2
            service_provider.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# Step 3: Services
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_services(request):
    """Add or update services."""
    try:
        service_provider = get_object_or_404(ServiceProvider, user=request.user)
        services_data = request.data.get('services', [])
        
        if not services_data:
            return Response({"error": "At least one service is required"}, 
                          status=status.HTTP_400_BAD_REQUEST)

        created_services = []
        for service_data in services_data:
            required_fields = ['name', 'price', 'duration']
            if any(field not in service_data for field in required_fields):
                return Response({"error": f"Missing required fields for service: {required_fields}"}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            service_data['provider'] = service_provider.id
            service_serializer = ServiceSerializer(data=service_data)
            if service_serializer.is_valid():
                service = service_serializer.save()
                created_services.append(service_serializer.data)
            else:
                return Response(service_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service_provider.onboarding_progress = 3
        service_provider.save()
        
        return Response({
            "message": "Services added successfully",
            "services": created_services
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# Step 4: Business Hours
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_business_hours(request):
    """Set business hours and slots."""
    try:
        service_provider = get_object_or_404(ServiceProvider, user=request.user)
        
        # Update general business hours
        opening_time = request.data.get('opening_time')
        closing_time = request.data.get('closing_time')
        if opening_time and closing_time:
            service_provider.opening_time = opening_time
            service_provider.closing_time = closing_time
            service_provider.save()

        # Update or create shop slots
        slot_data = {
            'provider': service_provider,
            'slot_interval': request.data.get('slot_interval', 30),
            'prebooking_rule': request.data.get('prebooking_rule', 'daily')
        }

        # Add working hours for each day
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            start_key = f'{day}_start'
            end_key = f'{day}_end'
            if start_key in request.data and end_key in request.data:
                slot_data[start_key] = request.data[start_key]
                slot_data[end_key] = request.data[end_key]

        shop_slot, created = ShopSlot.objects.update_or_create(
            provider=service_provider,
            defaults=slot_data
        )

        service_provider.onboarding_progress = 4
        service_provider.save()


        return Response({
            "message": "Business hours set successfully",
            "shop_slot": ShopSlotSerializer(shop_slot).data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Step 5: Team Size
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_team_size(request):
    """Set team size."""
    try:
        service_provider = get_object_or_404(ServiceProvider, user=request.user)
        
        team_size = request.data.get('team_size')
        if not team_size:
            return Response({"error": "Team size is required"}, status=status.HTTP_400_BAD_REQUEST)

        service_provider.team_size = team_size
        service_provider.onboarding_progress = 5
        service_provider.save()

        return Response({
            "message": "Team size updated successfully",
            "team_size": team_size
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Step 6: Booking Preferences
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_booking_preferences(request):
    """Set booking preferences and complete onboarding."""
    try:
        service_provider = get_object_or_404(ServiceProvider, user=request.user)
        
        booking_preferences = request.data.get('booking_preferences')
        if not booking_preferences:
            return Response({"error": "Booking preferences are required"}, 
                          status=status.HTTP_400_BAD_REQUEST)

        service_provider.booking_preferences = booking_preferences
        service_provider.is_onboarding_complete = True
        service_provider.onboarding_progress = 0  
        service_provider.save()

        return Response({
            "message": "Onboarding completed successfully",
            "booking_preferences": booking_preferences
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Get Onboarding Progress
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_onboarding_progress(request):
    """Get current onboarding progress."""
    try:
        service_provider = get_object_or_404(ServiceProvider, user=request.user)
        
        return Response({
            "current_step": service_provider.onboarding_progress,
            "is_complete": service_provider.is_onboarding_complete,
            "total_steps": 6
        }, status=status.HTTP_200_OK)
    
    except ServiceProvider.DoesNotExist:
        return Response({
            "error": "Service provider not found",
            "current_step": 0,
            "is_complete": False,
            "total_steps": 6
        }, status=status.HTTP_404_NOT_FOUND)