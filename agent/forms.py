from django import forms
# from django.forms import inlineformset_factory

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
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3})
        }

class AgentCreatePropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__'
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