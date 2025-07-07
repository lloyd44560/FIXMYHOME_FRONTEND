document.addEventListener('DOMContentLoaded', function() {
    // Triggers
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    // Form ID
    const agentForm = document.getElementById('agentForm');

    // ####################################################################################
    // Form Fields- Details
    const nameInput = document.getElementById('id_name');
    const emailInput = document.getElementById('id_email');
    const phoneInput = document.getElementById('id_phone');
    const contactPersonInput = document.getElementById('id_contact_person');
    const passwordInput = document.getElementById('id_password');
    const confirmPasswordInput = document.getElementById('id_confirm_password');

    // Validation Error Elements - Details
    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const phoneError = document.getElementById('phoneError');
    const contactPersonError = document.getElementById('contactPersonError');
    const passwordError = document.getElementById('passwordError');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    // ####################################################################################
    // Form Fields - Company
    const companyNameInput = document.getElementById('id_company_name');
    const companyAddressInput = document.getElementById('id_company_address');
    const agencyIDInput = document.getElementById('id_agency_id');
    const websiteInput = document.getElementById('id_website');
    const contractorLicenseInput = document.getElementById('id_contractor_license');
    const serviceInput = document.getElementById('id_service');

    // Validation Error Elements - Company
    const companyNameError = document.getElementById('companyNameError');
    const companyAddressError = document.getElementById('companyAddressError');
    const agentIDError = document.getElementById('agentIDError');
    const websiteError = document.getElementById('websiteError');
    const contractorLicenseError = document.getElementById('contractorLicenseError');
    const serviceError = document.getElementById('serviceError');

    // ####################################################################################
    // Form Fields - Rates
    const stateInput = document.getElementById('id_state');
    const municipalityInput = document.getElementById('id_municipality');
    const cityInput = document.getElementById('id_city');
    const addressOneInput = document.getElementById('id_address_line_1');
    const addressTwoInput = document.getElementById('id_address_line_2');
    const postalCodeInput = document.getElementById('id_postal_code');
    const gstCheckDpl = document.getElementById('gstCheckDpl');

    // Validation Error Elements - Rates
    const stateError = document.getElementById('rateState');
    const municipalityError = document.getElementById('rateMunicipality');
    const cityError = document.getElementById('rateCity');
    const addressOneError = document.getElementById('rateAddressOne');
    const addressTwoError = document.getElementById('rateAddressTwo');
    const postalError = document.getElementById('ratePostal');
    
    // Validation fields array for easy iteration
    const fields = [
        { id: nameInput, label: 'Name', error: nameError},
        { id: emailInput, label: 'Email', error: emailError},
        { id: phoneInput, label: 'Phone', error: phoneError},
        { id: contactPersonInput, label: 'Contact Person', error: contactPersonError},
        { id: agencyIDInput, label: 'Agent ID', error: agentIDError},
        { id: websiteInput, label: 'Website', error: websiteError},
        { id: passwordInput, label: 'Password', error: passwordError},
        { id: confirmPasswordInput, label: 'Confirm Password', error: confirmPasswordError},
        // ####################################################################################
        { id: companyNameInput, error: companyNameError, label: 'Company Name'},
        { id: companyAddressInput, error: companyAddressError, label: 'Company Address' },
        { id: contractorLicenseInput, error: contractorLicenseError, label: 'License Number'},
        { id: serviceInput, error: serviceError, label: 'Service'},
        // ####################################################################################
        { id: stateInput, error: stateError, label: 'State'},
        { id: municipalityInput, error: municipalityError, label: 'Municipality'},
        { id: cityInput, error: cityError, label: 'City'},
        { id: addressOneInput, error: addressOneError, label: 'Address Line One'},
        { id: addressTwoInput, error: addressTwoError, label: 'Address Line Two'},
        { id: postalCodeInput, error: postalError, label: 'Postal Code'},
    ];

    fields.forEach(field => {
        console.log(`Adding change event listener for ${field.label}`);
        const input = document.getElementById(field.id);
        if (input) {
            input.addEventListener('change', function() {
              console.log(`${field.label} changed:`, input.value);
              if (input.value.trim() !== '') {
                  console.log(`Clearing error for ${input.label}`);
                  input.error.textContent = '';
              } 
            });
        }
    });
    
    nextBtn.addEventListener('click', function(e) {
        if (!steps[currentStep].classList.contains('hidden') && currentStep < steps.length - 1) {
            if (currentStep === 0) { // Step 1 validation (Personal Details)
                // Regex for at least one number and one special character
                const specialCharRegex = /[!@#$%^&*(),.?":{}|<>_]/;
                const hasNumber = /\d/;
                const onlyNumbers = /^\d+$/;
                
                let hasError = false;

                // Validate Name Input
                if (nameInput.value.trim() === '') {
                    hasError = true;
                    nameError.textContent = 'Name is required!';
                    nameInput.focus();
                } else {
                    nameError.textContent = ''
                }

                // Validate Email Input
                if (emailInput.value.trim() === '') {
                    hasError = true;
                    emailError.textContent = 'Email is required!';
                    emailInput.focus();
                } else {
                    emailError.textContent = ''
                }

                // Validate Phone Input
                if (phoneInput.value.trim() === '') {
                    hasError = true;
                    phoneError.textContent = 'Phone number is required!';
                    phoneInput.focus();
                } else {
                    phoneError.textContent = ''
                }

                // Validate Contact Person Input
                if (contactPersonInput.value.trim() === '') {
                    hasError = true;
                    contactPersonError.textContent = 'Contact Person is required!';
                    contactPersonInput.focus();
                } else {
                    contactPersonError.textContent = ''
                }

                // Validate Password Input
                if (passwordInput.value.trim() === '') {
                    hasError = true;
                    passwordError.textContent = 'Password is required!';
                    passwordInput.focus();
                } else if (passwordInput.value.length < 8) {
                    hasError = true;
                    passwordError.textContent = 'Password must be at least 8 characters.';
                    passwordInput.focus();
                } else if (onlyNumbers.test(passwordInput.value)) {
                    hasError = true;
                    passwordError.textContent = 'Password cannot be only numbers.';
                    passwordInput.focus();
                } else if (!specialCharRegex.test(passwordInput.value)) {
                    hasError = true;
                    passwordError.textContent = 'Password must contain at least one special character.';
                    passwordInput.focus();
                } else if (!hasNumber.test(passwordInput.value)) {
                    console.log(!hasNumber.test(passwordInput.value), 'Has Number Test');
                    hasError = true;
                    passwordError.textContent = 'Password must contain at least one number.';
                    passwordInput.focus();
                } else {
                    passwordError.textContent = '';
                }
                
                // Validate Confirm Password Input
                if (passwordInput.value.trim() !== confirmPasswordInput.value.trim()) {
                    hasError = true;
                    confirmPasswordError.textContent = 'Passwords do not match!';
                    confirmPasswordInput.focus();
                } else {
                    confirmPasswordError.textContent = ''
                }

                // Check if all required fields are filled
                if (hasError) {
                    e.preventDefault();
                    return;

                } else {
                    currentStep++;
                    updateStep();
                }
                
            } else if (currentStep === 1) { // Step 2 validation (Company Details)
                let hasError = false;

                // Validate company name
                if (companyNameInput.value.trim() === '') {
                    hasError = true;
                    companyNameError.textContent = 'Name is required!';
                    companyNameInput.focus();
                } else {
                    companyNameError.textContent = ''
                }

                // Validate company address
                if (companyAddressInput.value.trim() === '') {
                    hasError = true;
                    companyAddressError.textContent = 'Company address is required!';
                    companyAddressInput.focus();
                } else {
                    companyAddressError.textContent = ''
                }

                // Validate Agent ID Input
                if (agencyIDInput.value.trim() === '') {
                    hasError = true;
                    e.preventDefault();
                    agentIDError.textContent = 'Agent ID is required!';
                    agencyIDInput.focus();
                } else {
                    agentIDError.textContent = ''
                }

                // Validate Website Input
                if (websiteInput.value.trim() === '') {
                    hasError = true;
                    e.preventDefault();
                    websiteError.textContent = 'Website is required!';
                    websiteInput.focus();
                } else {
                    websiteError.textContent = ''
                }

                // Validate License number
                if (contractorLicenseInput.value.trim() === '') {
                    hasError = true;
                    contractorLicenseError.textContent = 'License number is required';
                    contractorLicenseInput.focus();
                } else {
                    companyAddressError.textContent = ''
                }

                // Service
                if (serviceInput.value.trim() === '') {
                    hasError = true;
                    serviceError.textContent = 'Service is required!';
                    serviceInput.focus();
                } else {
                    serviceError.textContent = ''
                }

                // Check if all required fields are filled
                if (hasError) {
                    e.preventDefault();
                    return;

                } else {
                    currentStep++;
                    updateStep();
                }
            }  
        }
    });

    submitBtn.addEventListener('click', function(e) {
        if (currentStep === steps.length - 1) {
            if (currentStep === 2) {
                let hasError = false;

                // Validate State Input
                if (stateInput.value.trim() === '') {
                    hasError = true;
                    stateError.textContent = 'State is required!';
                    stateInput.focus();
                } else {
                    stateError.textContent = ''
                }

                // Validate Municipality Input
                if (municipalityInput.value.trim() === '') {
                    hasError = true;
                    municipalityError.textContent = 'Municipality is required!';
                    municipalityInput.focus();
                } else {
                    municipalityError.textContent = ''
                }

                // Validate City Input
                if (cityInput.value.trim() === '') {
                    hasError = true;
                    cityError.textContent = 'City is required!';
                    cityInput.focus();
                } else {
                    cityError.textContent = ''
                }

                // Validate Address Line 1 Input
                if (addressOneInput.value.trim() === '') {
                    hasError = true;
                    addressOneError.textContent = 'Address Line 1 is required!';
                    addressOneInput.focus();
                } else {
                    addressOneError.textContent = ''
                }

                // Validate Address Line 2 Input
                if (addressTwoInput.value.trim() === '') {
                    hasError = true;
                    addressTwoError.textContent = 'Address Line 2 is required!';
                    addressTwoInput.focus();
                } else {
                    addressTwoError.textContent = ''
                }

                // Validate Postal Code Input
                if (postalCodeInput.value.trim() === '') {
                    hasError = true;
                    postalError.textContent = 'Postal Code is required!';
                    postalCodeInput.focus();
                } else {
                    postalError.textContent = ''
                }
                
                if (hasError) {
                    e.preventDefault();
                    return;
                } else {
                    // Submit form
                    agentForm.submit()
                }
            }
        }
    });
});