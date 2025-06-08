const companyType = document.getElementById('id_company_type');

const soleTraderSection = document.getElementById('soleTraderSection');
const companySection = document.getElementById('companySection');
let step2Label = document.getElementById('step2-label');

if (companyType && step2Label) {
    companyType.addEventListener('change', function() {
        console.log(`${step2Label.textContent} changed:`, companyType.value);
        if (companyType.value.trim() === 'company') {
            step2Label.textContent = 'Company';
            companySection.classList.remove('hidden');
            soleTraderSection.classList.add('hidden');
        } else if (companyType.value.trim() === 'sole_trader') {
            step2Label.textContent = 'Sole Trader';
            companySection.classList.add('hidden');
            soleTraderSection.classList.remove('hidden');
        } else {
            step2Label.textContent = '';
        }
    });
}