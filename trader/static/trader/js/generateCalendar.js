// --- Calendar Functionality ---
const holidays = ['2024-06-10', '2024-06-17', '2024-06-26'];
const currentMonth = 5; // 0-indexed: June = 5
const currentYear = 2024;

function generateCalendar(year, month) {
    const calendar = document.getElementById('calendar');
    calendar.innerHTML = '';

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Add empty slots for days before the 1st
    for (let i = 0; i < firstDay; i++) {
        calendar.innerHTML += `<div></div>`;
    }

    // Add actual days
    for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const isHoliday = holidays.includes(dateStr);
    const isToday = new Date().toDateString() === new Date(year, month, day).toDateString();

    calendar.innerHTML += `
        <div class="
            w-8 h-8 mx-auto flex items-center justify-center rounded-full 
            ${isHoliday ? 'bg-blue-600 text-white font-semibold' : ''}
            ${isToday && !isHoliday ? 'bg-blue-100 text-blue-700' : ''}
            hover:bg-blue-200 cursor-pointer
            ">
            ${day}
        </div>`;
    }
}

// Initially render June 2024
generateCalendar(currentYear, currentMonth);