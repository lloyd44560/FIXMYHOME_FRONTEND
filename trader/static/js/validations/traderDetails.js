document.addEventListener('DOMContentLoaded', function() {
    // Triggers
    const nextBtn = document.getElementById('nextBtn');
    let step2Company = document.getElementById('step2-company');

    // Form Fields
    const nameInput = document.getElementById('id_name');
    const emailInput = document.getElementById('id_email');
    const phoneInput = document.getElementById('id_phone');
    const companyType = document.getElementById('id_company_type');
    const passwordInput = document.getElementById('id_password');
    const confirmPasswordInput = document.getElementById('id_confirm_password');
    
    // Validation Error Elements
    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const phoneError = document.getElementById('phoneError');
    const passwordError = document.getElementById('passwordError');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    const fields = [
        { id: 'id_name', label: 'Name', error: nameError },
        { id: 'id_email', label: 'Email', error: emailError },
        { id: 'id_phone', label: 'Phone', error: phoneError },
        { id: 'id_password', label: 'Password', error: passwordError },
        { id: 'id_confirm_password', label: 'Confirm Password', error: confirmPasswordError }
    ];

    fields.forEach(field => {
        const input = document.getElementById(field.id);
        if (input) {
            input.addEventListener('change', function() {
              console.log(`${field.label} changed:`, input.value);
              if (input.value.trim() !== '') {
                  field.error.textContent = '';
              } 
            });
        }
    });

    nextBtn.addEventListener('click', function(e) {
      if (!steps[currentStep].classList.contains('hidden') && currentStep < steps.length - 1) {
        // Validate Name Input
        if (nameInput.value.trim() === '') {
            e.preventDefault();
            document.getElementById('nameError').textContent = 'Name is required!';
            nameInput.focus();
        }

        // Validate Email Input
        if (emailInput.value.trim() === '') {
            e.preventDefault();
            document.getElementById('emailError').textContent = 'Email is required!';
            emailInput.focus();
        }

        // Validate Phone Input
        if (phoneInput.value.trim() === '') {
            e.preventDefault();
            document.getElementById('phoneError').textContent = 'Phone number is required!';
            phoneInput.focus();
        }
        // Validate Password Input
        if (passwordInput.value.trim() === '') {
            e.preventDefault();
            document.getElementById('passwordError').textContent = 'Password is required!';
            passwordInput.focus();
        }

        // Validate Confirm Password Input
        if (passwordInput.value.trim() !== confirmPasswordInput.value.trim()) {
            e.preventDefault();
            document.getElementById('confirmPasswordError').textContent = 'Passwords do not match!';
            confirmPasswordInput.focus();
            return;
        }
        
        // Check if all required fields are filled
        if (
          passwordInput.value.trim() !== '' && confirmPasswordInput.value.trim() !== '' && 
          nameInput.value.trim() !== '' && emailInput.value.trim() !== '' && phoneInput.value.trim() !== '' &&
          passwordInput.value.trim() === confirmPasswordInput.value.trim()
        ) 
        {
          // Clear any previous error messages
          nameError.textContent = '';
          emailError.textContent = '';
          phoneError.textContent = '';  
          passwordError.textContent = '';
          confirmPasswordError.textContent = '';

          // If company type is equal to 'company', show the company step
          if (companyType.value.trim() === 'company') {
            step2Company.classList.remove('hidden');
          }

          // Only proceed if the current step is visible
          currentStep++;
          updateStep();
        }
      }
  });
});