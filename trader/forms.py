from django import forms
from .models import TraderRegistration

class TraderRegistrationForm(forms.ModelForm):
    class Meta:
        model = TraderRegistration
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(),
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if TraderRegistration.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone