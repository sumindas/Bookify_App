import os
import random
import string
import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.gis.db import models as postgis
from django.utils import timezone
from django.utils.translation import gettext_lazy as _



def get_random_string():
    chars = string.ascii_lowercase
    strin = ''.join(random.choice(chars) for _ in range(6))
    date = datetime.datetime.now().strftime("%m%d%H%M%S")
    return 'f' + date + strin


class MyUserManager(BaseUserManager):

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('Username must be set')
        user = self.model(username = username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 1)
        extra_fields.setdefault('name', "Superuser")

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('user_type') != 1:
            raise ValueError('Superuser must have user_type=1.')
        return self._create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    def get_file_path(self, instance, filename):
        ext = filename.split('.')[-1]
        tmp = get_random_string()
        filename = "%s.%s" % (tmp, ext)
        return os.path.join('user', filename)

    TYPE_CHOICES = (
            (0, 'No Special Access'),
            (1, 'Admin'),
            (2, 'Customer'),
            (3, 'Partner'),
    )
    username = models.CharField(unique = True, max_length = 50,
                                error_messages = {
                                        'unique': _("A staff with this phone/email number already exists."), })
    name = models.CharField(max_length = 200, null = True, blank = True)
    phone = models.CharField(null = True, blank = True, max_length = 50)
    image = models.ImageField(upload_to = get_file_path, null = True, blank = True, default = 'user/default.jpg')
    user_type = models.IntegerField(default = 0, choices = TYPE_CHOICES)
    created = models.DateTimeField(default = timezone.now)
    is_deleted = models.BooleanField(default = False)
    is_staff = models.BooleanField(
            _('staff status'),
            default = False,
            help_text = _('Designates whether the staff can log into this site.'),
    )
    is_mobile = models.BooleanField(
            _('mobile verification'),
            default = False,
            help_text = _(
                    'Designates whether this user verified mobile number.'
            ),
    )
    USERNAME_FIELD = 'username'
    objects = MyUserManager()

    def _str_(self):
        if self.name:
            return self.name
        else:
            return self.username


class TempUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

class Otp(models.Model):
    code = models.CharField(max_length=6)
    request_id = models.CharField(max_length=255, unique=True)
    requested_by_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    temp_user = models.ForeignKey(TempUser, on_delete=models.CASCADE, blank=True, null=True)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

class ServiceCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='business_type_icons/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default = False)
    

class ServiceProvider(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    shop_type = models.CharField(max_length=50, choices=[('male', 'Male'), ('female', 'Female'), ('unisex', 'Unisex')])
    address = models.TextField()
    location = postgis.PointField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    team_size = models.IntegerField(default=1, help_text="Number of staff in the team.")
    booking_preferences = models.CharField(
        max_length=50,
        choices=[
            ('same-day', 'Same Day'),
            ('same-day-1', 'Same Day and 1 Day Before'),
            ('same-day-2', 'Same Day and 2 Days Before'),
            ('same-day-3', 'Same Day and 3 Days Before'),
        ],
        default='same-day'
    )
    onboarding_progress = models.IntegerField(default=0)  
    is_onboarding_complete = models.BooleanField(default=False)
    
    def __str__(self):
        return self.category.name or self.user.username

class ShopSlot(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    slot_interval = models.PositiveIntegerField(help_text="Duration of each slot in minutes")
    prebooking_rule = models.CharField(max_length=50, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    is_shop_available = models.BooleanField(default=True)
    monday_start = models.TimeField(blank=True, null=True)
    monday_end = models.TimeField(blank=True, null=True)
    tuesday_start = models.TimeField(blank=True, null=True)
    tuesday_end = models.TimeField(blank=True, null=True)
    wednesday_start = models.TimeField(blank=True, null=True)
    wednesday_end = models.TimeField(blank=True, null=True)
    thursday_start = models.TimeField(blank=True, null=True)
    thursday_end = models.TimeField(blank=True, null=True)
    friday_start = models.TimeField(blank=True, null=True)
    friday_end = models.TimeField(blank=True, null=True)
    saturday_start = models.TimeField(blank=True, null=True)
    saturday_end = models.TimeField(blank=True, null=True)
    sunday_start = models.TimeField(blank=True, null=True)
    sunday_end = models.TimeField(blank=True, null=True)
    

class Service(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")

class TimeSlot(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

class Booking(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])
    booking_type = models.CharField(max_length=50, choices=[('same-day', 'Same-Day'), ('premium', 'Premium')], blank=True, null=True)
    booking_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_service_price = models.DecimalField(max_digits=10, decimal_places=2)

class Offer(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.PositiveIntegerField()
    valid_from = models.DateField()
    valid_until = models.DateField()

class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

class UserFavorites(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=50, choices=[('booking_fee', 'Booking Fee'), ('full_payment', 'Full Payment')])
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')])
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_reference = models.CharField(max_length=255, unique=True)

class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    refunded_at = models.DateTimeField(default=timezone.now)
