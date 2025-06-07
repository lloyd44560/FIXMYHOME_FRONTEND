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
    step.classList.toggle('hidden', index !== currentStep);
    stepIndicators[index].classList.toggle('bg-blue-600', index === currentStep);
    stepIndicators[index].classList.toggle('text-white', index === currentStep);
    stepIndicators[index].classList.toggle('bg-gray-300', index !== currentStep);
    stepIndicators[index].classList.toggle('text-gray-600', index !== currentStep);
});

backBtn.disabled = currentStep === 0;

if (currentStep === steps.length - 1) {
    // Last step: hide Next, show Submit
    nextBtn.classList.add('hidden');
    submitBtn.classList.remove('hidden');
} else {
    // Other steps: show Next, hide Submit
    nextBtn.classList.remove('hidden');
    submitBtn.classList.add('hidden');
}
}

backBtn.addEventListener('click', () => {
if (currentStep > 0) {
    currentStep--;
    updateStep();
}
});

nextBtn.addEventListener('click', () => {
if (currentStep < steps.length - 1) {
    currentStep++;
    updateStep();
}
});

// Password toggle
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');
togglePassword.addEventListener('click', () => {
    if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    togglePassword.textContent = 'Hide';
    } else {
    passwordInput.type = 'password';
    togglePassword.textContent = 'Show';
    }
});

const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
const confirmPasswordInput = document.getElementById('confirmPassword');
toggleConfirmPassword.addEventListener('click', () => {
    if (confirmPasswordInput.type === 'password') {
    confirmPasswordInput.type = 'text';
    toggleConfirmPassword.textContent = 'Hide';
    } else {
    confirmPasswordInput.type = 'password';
    toggleConfirmPassword.textContent = 'Show';
    }
});

// Initialize
updateStep();