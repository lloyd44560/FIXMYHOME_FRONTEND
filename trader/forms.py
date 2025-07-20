from django import forms
from django.forms import inlineformset_factory

from .models import TraderRegistration
from .models import TeamMember
from .models import ContractorLicense
from .models import Jobs
from .models import Bidding

class TeamMemberForm(forms.ModelForm):
    holiday_date = forms.DateField(
        label="Confirm Password", 
        widget=forms.DateInput(attrs={'type': 'date'}), 
        required=False
    )

    class Meta:
        model = TeamMember
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={}),
            'active_postal_codes': forms.TextInput(attrs={'placeholder': '3070, 3071, 3072'}), 
            'labour_rate_per_hour': forms.NumberInput(attrs={'placeholder': 'XX.XX', 'step': '0.01', 'min': '0'}),
            'callout_rate': forms.NumberInput(attrs={'placeholder': 'XX.XX', 'step': '0.01', 'min': '0'}),
            'time_in': forms.TimeInput(attrs={'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'type': 'time'}),
            'holidayTime_in': forms.TimeInput(attrs={'type': 'time'}),
            'holidayTime_out': forms.TimeInput(attrs={'type': 'time'})
        }

TeamMemberFormSet = inlineformset_factory(
    TraderRegistration, TeamMember, form=TeamMemberForm,
    extra=1, can_delete=True
)

class ContractorLicenseForm(forms.ModelForm):
    class Meta:
        model = ContractorLicense
        fields = '__all__'

ContractorLicenseSet = inlineformset_factory(
    TraderRegistration, ContractorLicense, form=ContractorLicenseForm,
    extra=1, can_delete=True
)

class TraderRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={}),
        label="Confirm Password"
    )

    class Meta:
        model = TraderRegistration
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(attrs={}),
        }

    def clean(self):
        cleaned_data = super().clean()

class TraderEditProfileForm(forms.ModelForm):
    class Meta:
        model = TraderRegistration
        fields = '__all__'
        widgets = {}

class JobScheduleForm(forms.ModelForm):
    class Meta:
        model = Jobs
        exclude = ['agent']
        widgets = {
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

class BiddingForm(forms.ModelForm):
    class Meta:
        model = Bidding
        exclude = ['trader', 'is_approved', 'approved_at', 'approved_by', 'approval_notes', 'created_at']