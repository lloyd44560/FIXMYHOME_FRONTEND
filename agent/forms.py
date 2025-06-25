from django import forms
# from django.forms import inlineformset_factory

from .models import AgentRegister

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
            'notes': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'readonly': True}),  # Optional: lock email
        }