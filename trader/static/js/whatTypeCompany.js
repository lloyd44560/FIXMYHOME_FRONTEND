const companyType = document.getElementById('id_company_type');

let step2div = document.getElementById('step2-div');
let step2Indicator = document.getElementById('step2-indicator');
let step3Indicator = document.getElementById('step3-indicator');
let step4Indicator = document.getElementById('step4-indicator');
let step3Label = document.getElementById('step3-label');

if (companyType && step3Label) {
    companyType.addEventListener('change', function() {
        console.log(`${step3Label.textContent} changed:`, companyType.value);
        if (companyType.value.trim() === 'company') {
            step2Indicator.textContent = '2';
            step3Indicator.textContent = '3';
            step4Indicator.textContent = '4';
            step3Label.textContent = 'Team';

            if (step2div.classList.contains('hidden')) {
                step2div.classList.remove('hidden')
            }
        } else if (companyType.value.trim() === 'sole_trader') {
            step3Indicator.textContent = '2';
            step4Indicator.textContent = '3';
            step3Label.textContent = 'Sole Trader';
            step2div.classList.add('hidden')
        } else {
            step3Label.textContent = '';
        }
    });
}