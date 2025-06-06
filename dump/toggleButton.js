// Toggle active AM/PM
document.querySelectorAll('.toggle-btn').forEach(button => {
    button.addEventListener('click', () => {
    const container = button.parentElement;
    container.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-blue-100', 'text-blue-600');
    });
    button.classList.remove('bg-blue-100', 'text-blue-600');
    button.classList.add('bg-blue-600', 'text-white');
    });
});