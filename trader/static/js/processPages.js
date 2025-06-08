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
const uploadOption = document.getElementById('uploadOption');
const manualUploadFields = document.getElementById('manualUploadFields');

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
    // Only proceed if the current step is visible
    if (!steps[currentStep].classList.contains('hidden') && currentStep > 0) {
        currentStep--;
        updateStep();
    }
});

// Initialize
updateStep();