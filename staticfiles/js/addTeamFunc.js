// --- Add Team Member Functionality ---
const teamMemberNameInput = document.getElementById('teamMemberName');
const teamMemberPositionInput = document.getElementById('teamMemberPosition');
const addTeamMemberBtn = document.getElementById('addTeamMember');
const teamMemberList = document.getElementById('teamMemberList');

function updateTeamMemberHeader() {
    const header = document.getElementById('addedMembersHeader');
    const teamMemberList = document.getElementById('teamMemberList');
    // Show header only if there is at least one <li>
    header.classList.toggle('hidden', teamMemberList.querySelectorAll('li').length === 0);
}

function createTeamMemberItem(name, position) {
    const li = document.createElement('li');
    li.className = "flex items-center justify-between border p-2 rounded-md bg-gray-50";

    const span = document.createElement('span');
    span.className = "text-gray-800 font-medium";
    span.textContent = `${name} (${position})`;

    const controls = document.createElement('div');
    controls.className = "flex gap-2";

    const editBtn = document.createElement('button');
    editBtn.type = "button";
    editBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500 hover:text-blue-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11.5A1.5 1.5 0 005.5 20H17a2 2 0 002-2v-5m-5.586-4.586a2 2 0 112.828 2.828L11 17H8v-3l5.414-5.414z"/>
        </svg>
    `;
    editBtn.onclick = () => {
        teamMemberNameInput.value = name;
        teamMemberPositionInput.value = position;
        li.remove();
        updateTeamMemberHeader();
    };

    const deleteBtn = document.createElement('button');
    deleteBtn.type = "button";
    deleteBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500 hover:text-red-700" fill="none"
            viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M6 18L18 6M6 6l12 12"/>
        </svg>
    `;
    deleteBtn.onclick = () => {
        li.remove();
        updateTeamMemberHeader();
    };

    controls.appendChild(editBtn);
    controls.appendChild(deleteBtn);

    li.appendChild(span);
    li.appendChild(controls);

    return li;
}

addTeamMemberBtn.addEventListener('click', function () {
    const name = teamMemberNameInput.value.trim();
    const position = teamMemberPositionInput.value.trim();
    if (name && position) {
        teamMemberList.appendChild(createTeamMemberItem(name, position));
        teamMemberNameInput.value = '';
        teamMemberPositionInput.value = '';
        teamMemberNameInput.focus();
        updateTeamMemberHeader();
    }
});