from django import forms
from dashboard.models import ServiceProvider

class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = [
            'shop_name',
            'category',
            'shop_type',
            'address',
            'location',
            'opening_time',
            'closing_time',
            'team_size',
            'booking_preferences',
            'verification_documents'
        ]
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            'location': forms.HiddenInput(),  # Assuming you'll handle this with a map picker
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any custom field initialization here
        self.fields['category'].empty_label = "Select a category"
        
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})