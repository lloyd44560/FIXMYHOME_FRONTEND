from django import forms
from .models import Renter
from trader.models import Jobs
from agent.models.propertyAgent import Property
from .models import MinimumStandardReport
from .models import RenterRoom, RenterRoomAreaCondition
from .models import RoomApplianceReport


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
            'tenant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'audit_no': forms.TextInput(attrs={'class': 'form-control'}),
            'auditor': forms.TextInput(attrs={'class': 'form-control'}),
            'inspection_address': forms.TextInput(attrs={'class': 'form-control'}),
            'managing_agent': forms.TextInput(attrs={'class': 'form-control'}),
            'audit_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'audit_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'report_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class RenterRoomForm(forms.ModelForm):
    class Meta:
        model = RenterRoom
        fields = ['property', 'room_name', 'description']

class RenterRoomAreaConditionForm(forms.ModelForm):
    class Meta:
        model = RenterRoomAreaCondition
        fields = ['area_name', 'status', 'photo', 'remarks']
        widgets = {
            'area_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class RoomApplianceReportForm(forms.ModelForm):
    class Meta:
        model = RoomApplianceReport
        exclude = ['renter']
