from django import forms
from django.core.exceptions import ValidationError

from renter.models import Renter

# from django.forms import inlineformset_factory

from renter.models import Renter
from trader.models import Jobs, Bidding
from .models import AgentRegister, Property, Rooms

class CreateAgentFormClass(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={}),
        label="Confirm Password"
    )

    class Meta:
        model = AgentRegister
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(attrs={}),
        }

    def clean(self):
        cleaned_data = super().clean()

class AgentEditProfileForm(forms.ModelForm):
    class Meta:
        model = AgentRegister
        exclude = ['password']  # Exclude password only for editing
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3})
        }

class AgentCreatePropertyForm(forms.ModelForm):
    renter_name = forms.CharField(
        label="Renter Name",
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300 rounded-md p-2',
            'placeholder': 'Type renter name...'
        })
    )
    class Meta:
        model = Property
        exclude = ['agent']
        widgets = {
            'lease_start': forms.DateInput(attrs={
                'type': 'date',
            }),
            'lease_end': forms.DateInput(attrs={
                'type': 'date',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        renter_name = cleaned_data.get('renter_name')
        if renter_name:
            renter_qs = Renter.objects.filter(name__iexact=renter_name)
            if not renter_qs.exists():
                raise ValidationError({
                    'renter_name': "Renter not found. Would you like to send an invitation?"
                })
            # Optionally, set the FK if found
            self.instance.renter = renter_qs.first()
        return cleaned_data

class InvitationForm(forms.Form):
    name = forms.CharField(max_length=100, label="Renter Name")
    email = forms.EmailField(label="Renter Email")

class AgentCreateRoomForm(forms.ModelForm):
    class Meta:
        model = Rooms
        exclude = ['property']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }

class RenterUpdateForm(forms.ModelForm):
    class Meta:
        model = Renter
        exclude = ['user', 'password']  # exclude sensitive fields unless needed
        widgets = {
            'rooms': forms.Textarea(attrs={'rows': 3}),
        }

class AgentCreateJobForm(forms.ModelForm):
    class Meta:
        model = Jobs
        fields = ['renter', 'trader', 'notes', 'scheduled_at', 'priority']  # agent will be set in view

        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full border border-gray-300 rounded-md p-2'
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full border border-gray-300 rounded-md p-2'
            }),
            'priority': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded'
            }),
        }

        labels = {
            'priority': 'Mark as High Priority',
        }

class BiddingApprovalForm(forms.ModelForm):
    class Meta:
        model = Bidding
        fields = ['is_approved', 'approval_notes']
        widgets = {
            'approval_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Approval notes (optional)'}),
        }