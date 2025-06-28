document.addEventListener('DOMContentLoaded', function() {
    // Triggers
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    // Form ID
    const traderForm = document.getElementById('traderForm');

    // ####################################################################################
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

    // ####################################################################################
    // Form Fields - Company
    const companyNameInput = document.getElementById('id_company_name');
    const companyAddressInput = document.getElementById('id_company_address');
    const companyEmailInput = document.getElementById('id_company_email');
    const contractorLicenseInput = document.querySelector('input[name$="-contractorLicense"]');
    const abnInput = document.getElementById('id_abn');
    const industryInput = document.getElementById('id_industry');
    let gst_registered = document.getElementById('id_gst_registered');

    // Validation Error Elements - Company
    const companyNameError = document.getElementById('companyNameError');
    const companyAddressError = document.getElementById('companyAddressError');
    const companyEmailError = document.getElementById('companyEmailError');
    const contractorLicenseError = document.getElementById('contractorLicenseError');
    const abnError = document.getElementById('abnError');
    const industryError = document.getElementById('industryError');

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
        { id: nameInput, label: 'Name', error: nameError },
        { id: emailInput, label: 'Email', error: emailError },
        { id: phoneInput, label: 'Phone', error: phoneError },
        { id: passwordInput, label: 'Password', error: passwordError },
        { id: confirmPasswordInput, label: 'Confirm Password', error: confirmPasswordError },
        // ####################################################################################
        { id: companyNameInput, error: companyNameError, label: 'Company Name' },
        { id: companyAddressInput, error: companyAddressError, label: 'Company Address' },
        { id: companyEmailInput, error: companyEmailError, label: 'Company Email' }, 
        { id: contractorLicenseInput, error: contractorLicenseError, label: 'Contractor License Number' },
        { id: abnInput, error: abnError, label: 'ABN' },
        { id: industryInput, error: industryError, label: 'Industry Expertise' },
        // ####################################################################################
        { id: stateInput, error: stateError, label: 'State' },
        { id: municipalityInput, error: municipalityError, label: 'Municipality' },
        { id: cityInput, error: cityError, label: 'City' },
        { id: addressOneInput, error: addressOneError, label: 'Address Line One' },
        { id: addressTwoInput, error: addressTwoError, label: 'Address Line Two' },
        { id: postalCodeInput, error: postalError, label: 'Postal Code' },
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
                let hasError = false;

                // Validate Name Input
                if (nameInput.value.trim() === '') {
                    hasError = true;
                    e.preventDefault();
                    nameError.textContent = 'Name is required!';
                    nameInput.focus();
                } else {
                    nameError.textContent = ''
                }

                // Validate Email Input
                if (emailInput.value.trim() === '') {
                    hasError = true;
                    e.preventDefault();
                    emailError.textContent = 'Email is required!';
                    emailInput.focus();
                } else {
                    emailError.textContent = ''
                }

                // Validate Phone Input
                if (phoneInput.value.trim() === '') {
                    hasError = true;
                    e.preventDefault();
                    phoneError.textContent = 'Phone number is required!';
                    phoneInput.focus();
                } else {
                    phoneError.textContent = ''
                }

                // Validate Password Input
                if (passwordInput.value.trim() === '') {
                    hasError = true;
                    e.preventDefault();
                    passwordError.textContent = 'Password is required!';
                    passwordInput.focus();
                } else {
                    passwordError.textContent = ''
                }

                // Validate Confirm Password Input
                if (passwordInput.value.trim() !== confirmPasswordInput.value.trim()) {
                    hasError = true;
                    e.preventDefault();
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
                    // Skip company step if sole_trader, else go to company step
                    if (companyType && companyType.value === 'sole_trader') {
                        currentStep += 2; // Skip company step
                    } else {
                        currentStep += 1; // Go to company step
                    }
                    updateStep();
                }
                
            } else if (currentStep === 1) { // Step 2 validation (company type || solo trader)
                let hasError = false;

                // Validate company name
                if (companyNameInput.value.trim() === '') {
                    hasError = true;
                    companyNameError.textContent = 'Company Name is required!';
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

                // Validate company email
                if (companyEmailInput.value.trim() === '') {
                    hasError = true;
                    companyEmailError.textContent = 'Company email is required!';
                    companyEmailInput.focus();
                } else {
                    companyEmailError.textContent = ''
                }

                // Validate contractor license
                if (contractorLicenseInput.value.trim() === '') {
                    hasError = true;
                    contractorLicenseError.textContent = 'Contractor license number is required!';
                    contractorLicenseInput.focus();
                } else {
                    contractorLicenseError.textContent = ''
                }

                // Validate ABN
                if (abnInput.value.trim() === '') {
                    hasError = true;
                    abnError.textContent = 'ABN is required!';
                    abnInput.focus();
                } else {
                    abnError.textContent = ''
                }

                // Validate industry expertise
                if (industryInput.value.trim() === '') {
                    hasError = true;
                    industryError.textContent = 'Industry expertise is required!';
                    industryInput.focus();
                } else {
                    industryError.textContent = ''
                }

                if (hasError) {
                    e.preventDefault();
                    return;
                } else {
                    // Only proceed if the current step is visible
                    currentStep++;
                    updateStep();
                }

            } else if (currentStep === 2) { // Step 3 validation (teams)
                // Get all team member forms by their Django-generated IDs
                const teamNameInputs = document.querySelectorAll('input[name$="-name"]');
                const teamPositionInputs = document.querySelectorAll('input[name$="-position"]');
                const empPostalInputs = document.querySelectorAll('input[name$="-active_postal_codes"]');
                const teamTimeInInputs = document.querySelectorAll('input[name$="-time_in"]');
                const teamTimeOutInputs = document.querySelectorAll('input[name$="-time_out"]');

                let hasError = false;

                teamNameInputs.forEach((input) => {
                    const errorSpan = input.parentElement.querySelector('.text-red-500.text-xs');
                    if (input.value.trim() === '') {
                        hasError = true;
                        if (errorSpan) errorSpan.textContent = 'Team member name is required!';
                        input.focus();
                    } else if (errorSpan) {
                        errorSpan.textContent = '';
                    }
                });

                teamPositionInputs.forEach((input) => {
                    const errorSpan = input.parentElement.querySelector('.text-red-500.text-xs');
                    if (input.value.trim() === '') {
                        hasError = true;
                        if (errorSpan) errorSpan.textContent = 'Position is required!';
                        input.focus();
                    } else if (errorSpan) {
                        errorSpan.textContent = '';
                    }
                });

                empPostalInputs.forEach((input) => {
                    const errorSpan = input.parentElement.querySelector('.text-red-500.text-xs');
                    if (input.value.trim() === '') {
                        hasError = true;
                        if (errorSpan) errorSpan.textContent = 'Postal code is required!';
                        input.focus();
                    } else if (errorSpan) {
                        errorSpan.textContent = '';
                    }
                });

                teamTimeInInputs.forEach((input) => {
                    const errorSpan = input.parentElement.querySelector('.text-red-500.text-xs');
                    if (input.value.trim() === '') {
                        hasError = true;
                        if (errorSpan) errorSpan.textContent = 'Time in is required!';
                        input.focus();
                    } else if (errorSpan) {
                        errorSpan.textContent = '';
                    }
                });

                teamTimeOutInputs.forEach((input) => {
                    const errorSpan = input.parentElement.querySelector('.text-red-500.text-xs');
                    if (input.value.trim() === '') {
                        hasError = true;
                        if (errorSpan) errorSpan.textContent = 'Time out is required!';
                        input.focus();
                    } else if (errorSpan) {
                        errorSpan.textContent = '';
                    }
                });

                if (hasError) {
                    e.preventDefault();
                    return;
                }

                // If all validations pass, proceed to next step
                currentStep++;
                updateStep();
            }  else {
                // For other steps, just proceed
                currentStep++;
                updateStep();
            }
        }
    });

    submitBtn.addEventListener('click', function(e) {
        if (currentStep === steps.length - 1) {
            if (currentStep === 3) {
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
                    // Fill GST Field
                    if (gstCheckDpl) {
                        gst_registered.checked = true;
                    }
                    // Submit form
                    traderForm.submit()
                }
            }
        }
    });
});