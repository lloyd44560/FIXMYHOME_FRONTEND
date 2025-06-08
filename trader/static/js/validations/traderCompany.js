document.addEventListener('DOMContentLoaded', function() {
    const nextBtn = document.getElementById('nextBtn');

    // Company Fields
    const companyNameInput = document.getElementById('id_company_name');
    const companyAddressInput = document.getElementById('id_company_address');
    const companyEmailInput = document.getElementById('id_company_email');
    const companyLandlineInput = document.getElementById('id_company_landline');
    const contractorLicenseInput = document.getElementById('id_contractor_license');
    const abnInput = document.getElementById('id_abn');
    const industryInput = document.getElementById('id_industry');

    // Error Elements
    const companyNameError = document.getElementById('companyNameError');
    const companyAddressError = document.getElementById('companyAddressError');
    const companyEmailError = document.getElementById('companyEmailError');
    const companyLandlineError = document.getElementById('companyLandlineError');
    const contractorLicenseError = document.getElementById('contractorLicenseError');
    const abnError = document.getElementById('abnError');
    const industryError = document.getElementById('industryError');

    // Validation fields array for easy iteration
    const fields = [
        { input: companyNameInput, error: companyNameError, label: 'Company Name' },
        { input: companyAddressInput, error: companyAddressError, label: 'Company Address' },
        { input: companyEmailInput, error: companyEmailError, label: 'Company Email' }, 
        { input: companyLandlineInput, error: companyLandlineError, label: 'Company Landline' }, 
        { input: contractorLicenseInput, error: contractorLicenseError, label: 'Contractor License Number' },
        { input: abnInput, error: document.getElementById('abnError'), label: 'ABN' },
        { input: industryInput, error: document.getElementById('industryError'), label: 'Industry Expertise' },
    ];

    // Clear error on change
    fields.forEach(field => {
        if (field.input) {
            field.input.addEventListener('change', function() {
                if (field.input.value.trim() !== '') {
                    field.error.textContent = '';
                }
            });
        }
    });

    nextBtn.addEventListener('click', function(e) {
        if (!steps[currentStep].classList.contains('hidden') && currentStep < steps.length - 1) {
            // Validate company name
            if (companyNameInput.value.trim() === '') {
                e.preventDefault();
                document.getElementById('nameError').textContent = 'Name is required!';
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
        }
    });
});