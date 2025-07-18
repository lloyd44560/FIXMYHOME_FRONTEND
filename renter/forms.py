from django import forms
from .models import Renter
from trader.models import Jobs
from agent.models.propertyAgent import Property
from .models import MinimumStandardReport
from .models import RenterRoom, RenterRoomAreaCondition
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


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'city': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'state': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'address': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2', 'rows': 3}),
            'renter_name': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'renter_contact': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'rent': forms.NumberInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'property_photo': forms.FileInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'condition_report': forms.FileInput(attrs={'class': 'w-full border rounded px-3 py-2'}),

            # Dropdowns
            'status': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'agent': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),

            # Dates
            'lease_start': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
            'lease_end': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
        }

class MinimumStandardReportForm(forms.ModelForm):
    class Meta:
        model = MinimumStandardReport
        exclude = ['renter']
        widgets = {
            'audit_date': forms.DateInput(attrs={'type': 'date'}),
        }



class RenterRoomForm(forms.ModelForm):
    class Meta:
        model = RenterRoom
        fields = ['property', 'room_name', 'description']

class RenterRoomAreaConditionForm(forms.ModelForm):
    class Meta:
        model = RenterRoomAreaCondition
        fields = ['area_name', 'status']
