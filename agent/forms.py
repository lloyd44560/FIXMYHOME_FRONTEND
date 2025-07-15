from django import forms
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['renter'].required = True
        self.fields['trader'].required = True
        self.fields['scheduled_at'].required = True
        self.fields['priority'].required = False
        self.fields['notes'].required = False

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class BiddingApprovalForm(forms.ModelForm):
    class Meta:
        model = Bidding
        fields = ['is_approved', 'approval_notes']
        widgets = {
            'approval_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Approval notes (optional)'}),
        }