// Tracking the current steps 
  const steps = [document.getElementById('step1'), document.getElementById('step2'), document.getElementById('step3')];
  const stepIndicators = [
    document.getElementById('step1-indicator'),
    document.getElementById('step2-indicator'),
    document.getElementById('step3-indicator'),
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

    // Show manual upload fields only if on step 3 and option selected
    if (currentStep === 2) {
      if (uploadOption.value === 'manual') {
        manualUploadFields.classList.remove('hidden');
      } else {
        manualUploadFields.classList.add('hidden');
      }
    } else {
      manualUploadFields.classList.add('hidden');
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

  uploadOption.addEventListener('change', () => {
      if (currentStep === 2) {
        if (uploadOption.value === 'manual') {
          manualUploadFields.classList.remove('hidden');
          reportUploadFields.classList.add('hidden');
        } else if (uploadOption.value === 'report') {
          manualUploadFields.classList.add('hidden');
          reportUploadFields.classList.remove('hidden');
        } else {
          manualUploadFields.classList.add('hidden');
          reportUploadFields.classList.add('hidden');
        }
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

    const roomInput = document.getElementById('roomType');
    const addRoomBtn = document.getElementById('addRoomBtn');
    const roomList = document.getElementById('roomList');

    function createRoomItem(roomName) {
      const li = document.createElement('li');
      li.className = "flex items-center justify-between border p-3 rounded-md";

      const span = document.createElement('span');
      span.className = "text-gray-800 font-medium";
      span.textContent = roomName;

      const controls = document.createElement('div');
      controls.className = "flex gap-3";

      const editBtn = document.createElement('button');
      editBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 hover:text-blue-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11.5A1.5 1.5 0 005.5 20H17a2 2 0 002-2v-5m-5.586-4.586a2 2 0 112.828 2.828L11 17H8v-3l5.414-5.414z"/>
        </svg>
      `;

      editBtn.onclick = () => {
        roomInput.value = span.textContent;
        li.remove();
      };

      const deleteBtn = document.createElement('button');
      deleteBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 hover:text-red-700" fill="none"
            viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M6 18L18 6M6 6l12 12"/>
        </svg>
      `;
      deleteBtn.onclick = () => li.remove();

      controls.appendChild(editBtn);
      controls.appendChild(deleteBtn);

      li.appendChild(span);
      li.appendChild(controls);

      return li;
    }

    addRoomBtn.addEventListener('click', () => {
      const roomName = roomInput.value.trim();
      if (roomName) {
        roomList.appendChild(createRoomItem(roomName));
        roomInput.value = '';
      }
    });


// Form validation Here for required  fielda based on proposal 
  const nameInput = document.getElementById("name");
  const nameError = document.getElementById("nameError");
  function validateFields() {
    const fields = [
      { id: "name", error: "nameError" },
      { id: "email", error: "emailError" },
      { id: "phone", error: "phoneError" },
      { id: "password", error: "passwordError" },
      { id: "confirmPassword", error: "confirmPasswordError" },
      { id: "company", error: "companyError" },
      { id: "contactPerson", error: "contactPersonError" },
      { id: "contactPersonEmail", error: "contactPersonEmailError" },
      { id: "contactPhone", error: "contactPhoneError" },
      { id: "state", error: "stateError" },
      { id: "city", error: "cityError" },
      { id: "zip", error: "zipError" },
      { id: "companyAddressLine1", error: "companyAddressLine1Error" },
      { id: "companyAddressLine2", error: "companyAddressLine2Error" },
    ];

    fields.forEach(({ id, error }) => {
      const input = document.getElementById(id);
      const errorMsg = document.getElementById(error);

      if (input && errorMsg) {
        if (input.value.trim() === "") {
          input.classList.add("border-red-500");
          errorMsg.classList.remove("hidden");
        } else {
          input.classList.remove("border-red-500");
          errorMsg.classList.add("hidden");
        }
      }
    });

    // Password match validation
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirmPassword").value.trim();
    const matchError = document.getElementById("matchError");

    if (password && confirmPassword && password !== confirmPassword) {
      matchError.classList.remove("hidden");
      document.getElementById("confirmPassword").classList.add("border-red-500");
    } else {
      matchError.classList.add("hidden");
      document.getElementById("confirmPassword").classList.remove("border-red-500");
    }
  }
  
document.getElementById("registrationForm").addEventListener("submit", function (e) {

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const nameInput = document.getElementById("name");
  const nameError = document.getElementById("nameError");

  //  Empty field check
  if (!name || !email || !password || !confirmPassword) {
    Swal.fire({
      icon: 'warning',
      title: 'Missing Fields',
      text: 'Please fill out all fields.',
    });
    return;
  }

  if (password !== confirmPassword) {
    Swal.fire({
      icon: 'error',
      title: 'Password Mismatch',
      text: 'Passwords do not match. Please try again.',
    });
    return;
  }


  Swal.fire({
    icon: 'success',
    title: 'Success!',
    text: 'Registration successful!',
  }).then(() => {
    // Optional: submit form manually or reset
    e.target.submit(); // Uncomment if using server-side

  });
});


 function openModal(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.remove('hidden');
      }
    }

    function closeModal(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('hidden');
      }
    }