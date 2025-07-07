from django import forms
from .models import Renter
from trader.models import Jobs

class RenterForm(forms.ModelForm):
    confirmPassword = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = Renter
        fields = [
            'name', 'email', 'phone', 'password',
            'company_name', 'contact_person', 'contact_person_email', 'contact_phone',
            'state', 'city', 'zip_code', 'company_address_line1', 'company_address_line2', 'company_postal_code',
            'upload_option',
            'property_image', 'floor_count', 'room_count',
            'address_line1', 'address_line2', 'house_state', 'house_city', 'house_zip',
            'rooms'
        ]
        widgets = {
            'password': forms.PasswordInput(),
            'rooms': forms.Textarea(attrs={'rows':3}),  # JSON input can be a textarea or better handled with JS
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirmPassword')

        if password != confirm_password:
            self.add_error('confirmPassword', "Passwords do not match")



class JobForm(forms.ModelForm):
    class Meta:
        model = Jobs
        fields = ['agent', 'trader', 'priority', 'status', 'notes']