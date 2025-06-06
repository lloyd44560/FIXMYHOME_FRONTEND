from django.shortcuts import render
from django.shortcuts import redirect

from .forms import TraderRegistrationForm

# View for the registration page
def register(request):
    return render(request, 'register.html')

def createRegisterTrader(request):
    print("createRegisterTrader called", request.method)
    if request.method == 'POST':
        form = TraderRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Replace with your success URL or page
    else:
        form = TraderRegistrationForm()
    return render(request, 'register.html', {'form': form})