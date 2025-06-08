document.addEventListener('DOMContentLoaded', function() {
    // Triggers
    const nextBtn = document.getElementById('nextBtn');

    // Form Fields- Details
    const nameInput = document.getElementById('id_name');
    const emailInput = document.getElementById('id_email');
    const phoneInput = document.getElementById('id_phone');
    const passwordInput = document.getElementById('id_password');
    const confirmPasswordInput = document.getElementById('id_confirm_password');

    // Validation Error Elements - Details
    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const phoneError = document.getElementById('phoneError');
    const passwordError = document.getElementById('passwordError');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    // Form Fields - Company
    const companyNameInput = document.getElementById('id_company_name');
    const companyAddressInput = document.getElementById('id_company_address');
    const companyEmailInput = document.getElementById('id_company_email');
    const companyLandlineInput = document.getElementById('id_company_landline');
    const contractorLicenseInput = document.getElementById('id_contractor_license');
    const abnInput = document.getElementById('id_abn');
    const industryInput = document.getElementById('id_industry');

    // Validation Error Elements - Company
    const companyNameError = document.getElementById('companyNameError');
    const companyAddressError = document.getElementById('companyAddressError');
    const companyEmailError = document.getElementById('companyEmailError');
    const companyLandlineError = document.getElementById('companyLandlineError');
    const contractorLicenseError = document.getElementById('contractorLicenseError');
    const abnError = document.getElementById('abnError');
    const industryError = document.getElementById('industryError');
    
    
    // Validation fields array for easy iteration
    const fields = [
        { id: nameInput, label: 'Name', error: nameError },
        { id: emailInput, label: 'Email', error: emailError },
        { id: phoneInput, label: 'Phone', error: phoneError },
        { id: passwordInput, label: 'Password', error: passwordError },
        { id: confirmPasswordInput, label: 'Confirm Password', error: confirmPasswordError },

        { id: companyNameInput, error: companyNameError, label: 'Company Name' },
        { id: companyAddressInput, error: companyAddressError, label: 'Company Address' },
        { id: companyEmailInput, error: companyEmailError, label: 'Company Email' }, 
        { id: companyLandlineInput, error: companyLandlineError, label: 'Company Landline' }, 
        { id: contractorLicenseInput, error: contractorLicenseError, label: 'Contractor License Number' },
        { id: abnInput, error: abnError, label: 'ABN' },
        { id: industryInput, error: industryError, label: 'Industry Expertise' },
    ];

    fields.forEach(field => {
        console.log(`Adding change event listener for ${field.label}`);
        const input = document.getElementById(field.id);
        if (input) {
            input.addEventListener('change', function() {
              console.log(`${field.label} changed:`, input.value);
              if (input.value.trim() !== '') {
                  console.log(`Clearing error for ${field.label}`);
                  field.error.textContent = '';
              } 
            });
        }
    });
    
    nextBtn.addEventListener('click', function(e) {
        if (!steps[currentStep].classList.contains('hidden') && currentStep < steps.length - 1) {
            if (currentStep === 0) { // Step 1 validation (personal details)
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

                    // Only proceed if the current step is visible
                    currentStep++;
                    updateStep();
                }
            } else if (currentStep === 1) { // Step 2 validation (company type || solo trader)
                // Validate company name
                if (companyNameInput.value.trim() === '') {
                    e.preventDefault();
                    companyNameError.textContent = 'Name is required!';
                    companyNameInput.focus();
                }

                // Validate company address
                if (companyAddressInput.value.trim() === '') {
                    e.preventDefault();
                    companyAddressError.textContent = 'Company address is required!';
                    companyAddressInput.focus();
                }

                // Validate company email
                if (companyEmailInput.value.trim() === '') {
                    e.preventDefault();
                    companyEmailError.textContent = 'Company email is required!';
                    companyEmailInput.focus();
                }

                // Validate company landline
                if (companyLandlineInput.value.trim() === '') {
                    e.preventDefault();
                    companyLandlineError.textContent = 'Company landline is required!';
                    companyLandlineInput.focus();
                }

                // Validate contractor license
                if (contractorLicenseInput.value.trim() === '') {
                    e.preventDefault();
                    contractorLicenseError.textContent = 'Contractor license number is required!';
                    contractorLicenseInput.focus();
                }

                // Validate ABN
                if (abnInput.value.trim() === '') {
                    e.preventDefault();
                    abnError.textContent = 'ABN is required!';
                    abnInput.focus();
                }

                // Validate industry expertise
                if (industryInput.value.trim() === '') {
                    e.preventDefault();
                    industryError.textContent = 'Industry expertise is required!';
                    industryInput.focus();
                }

                // Check if all required fields are filled
                if (
                    companyNameInput.value.trim() !== '' && companyAddressInput.value.trim() !== '' && 
                    companyEmailInput.value.trim() !== '' && companyLandlineInput.value.trim() !== '' && 
                    contractorLicenseInput.value.trim() !== '' && abnInput.value.trim() !== '' && 
                    industryInput.value.trim() !== ''
                ) 
                {
                    // Clear any previous error messages
                    companyNameError.textContent = '';
                    companyAddressError.textContent = '';
                    companyEmailError.textContent = '';
                    companyLandlineError.textContent = '';
                    contractorLicenseError.textContent = '';
                    abnError.textContent = '';
                    industryError.textContent = '';

                    // Only proceed if the current step is visible
                    currentStep++;
                    updateStep();
                }
            } else {
                // For other steps, just proceed
                currentStep++;
                updateStep();
            }
        }
    });
});