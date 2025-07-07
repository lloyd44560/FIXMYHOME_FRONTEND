// Password toggle
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('id_password');
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
const confirmPasswordInput = document.getElementById('id_confirm_password');
toggleConfirmPassword.addEventListener('click', () => {
    if (confirmPasswordInput.type === 'password') {
        confirmPasswordInput.type = 'text';
        toggleConfirmPassword.textContent = 'Hide';
    } else {
        confirmPasswordInput.type = 'password';
        toggleConfirmPassword.textContent = 'Show';
    }
});