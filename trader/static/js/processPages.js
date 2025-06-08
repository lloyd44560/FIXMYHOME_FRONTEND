const steps = [
    document.getElementById('step1'), 
    document.getElementById('step2'), 
    document.getElementById('step3'), 
    document.getElementById('step4')
];
const stepIndicators = [
    document.getElementById('step1-indicator'),
    document.getElementById('step2-indicator'),
    document.getElementById('step3-indicator'),
    document.getElementById('step4-indicator'),
];

const backBtn = document.getElementById('backBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn'); // New Submit button
let step2Company = document.getElementById('step2-company');

let currentStep = 0;

function updateStep() {
    steps.forEach((step, index) => {
        if (step) {
            step.classList.toggle('hidden', index !== currentStep);
        }

        if (stepIndicators[index]) {
            stepIndicators[index].classList.toggle('bg-blue-600', index === currentStep);
            stepIndicators[index].classList.toggle('text-white', index === currentStep);
            stepIndicators[index].classList.toggle('bg-gray-300', index !== currentStep);
            stepIndicators[index].classList.toggle('text-gray-600', index !== currentStep);
        }
    });
    // Show/hide step2-company based on step and company_type value
    if (step2Company && companyType) {
        if (currentStep === 1 && companyType.value === 'company') {
            step2Company.classList.remove('hidden');
            // Optionally show the indicator for company step
            if (stepIndicators[1]) stepIndicators[1].classList.remove('hidden');
        } else {
            step2Company.classList.add('hidden');
        }
    }

    if (backBtn) backBtn.disabled = currentStep === 0;

    if (currentStep === steps.length - 1) {
        nextBtn.classList.add('hidden');
        submitBtn.classList.remove('hidden');
    } else {
        nextBtn.classList.remove('hidden');
        submitBtn.classList.add('hidden');
    }
}

backBtn.addEventListener('click', () => {
    console.log(`Current step: ${currentStep + 1} of ${steps.length}`);
    // Only proceed if the current step is visible
    if (!steps[currentStep].classList.contains('hidden') && currentStep > 0) {
        currentStep--;
        updateStep();
    }
});

// Initialize
updateStep();