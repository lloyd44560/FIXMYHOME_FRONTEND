const companyType = document.getElementById('id_company_type');

let step2div = document.getElementById('step2-div');
let step3Indicator = document.getElementById('step3-indicator');
let step4Indicator = document.getElementById('step4-indicator');
let step3Label = document.getElementById('step3-label');

// Sole Trader form modification
let IsWorkInHoliday = document.getElementById('id_IsWorkInHoliday');
let holidayTime_in = document.getElementById('holidayTimeIn_div');
let holidayTime_out = document.getElementById('holidayTimeOut_div');
let postalNums = document.getElementById('postal_nums');
let timeIn = document.getElementById('timeIn');
let timeOut = document.getElementById('timeOut');
let wrkInholiday = document.getElementById('wrkInholiday');
let contactLabel = document.getElementById('contactLabel');
let emailLabel = document.getElementById('emailLabel');

if (companyType && step3Label) {
    companyType.addEventListener('change', function() {
        if (companyType.value.trim() === 'company') {
            step3Indicator.textContent = '3';
            step4Indicator.textContent = '4';
            step3Label.textContent = 'Team';
            postalNums.textContent = 'Active postal codes';
            contactLabel.textContent = 'Employee contact number (if available)';
            emailLabel.textContent = 'Employee email (if available)';
            timeIn.textContent = 'Employee time-in';
            timeOut.textContent = 'Employee time-out';

            wrkInholiday.classList.add('hidden')
            holidayTime_in.classList.add('hidden')
            holidayTime_out.classList.add('hidden')

            if (step2div.classList.contains('hidden')) {
                step2div.classList.remove('hidden')
            }
        } else if (companyType.value.trim() === 'sole_trader') {
            step2div.classList.add('hidden')
            step3Indicator.textContent = '2';
            step4Indicator.textContent = '3';
            step3Label.textContent = 'Sole Trader';            
            postalNums.textContent = 'Industry Service Post Code (active postal codes)';
            contactLabel.textContent = 'Contact number (if available)';
            emailLabel.textContent = 'Email (if available)';
            timeIn.textContent = 'Time-in';
            timeOut.textContent = 'Time-out';

            wrkInholiday.classList.remove('hidden')
            holidayTime_in.classList.remove('hidden')
            holidayTime_out.classList.remove('hidden')

            if (soleTraderHoliday.classList.contains('hidden')) {
                step2div.classList.remove('hidden');
            }
        } else {
            step3Label.textContent = '';
        }
    });
}