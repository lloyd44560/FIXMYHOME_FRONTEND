// Script to collect the rooms stated in the Condition Report
    function collectRoomData() {
    const roomData = [];
    const roomBlocks = document.querySelectorAll("#roomContainer .mb-6");

    roomBlocks.forEach(roomDiv => {
    const photoInput = roomDiv.querySelector('.room-photo-input');
    const photoFile = photoInput ? photoInput.files[0] : null;

    const categoryName = roomDiv.querySelector(".category-name").textContent.trim();
    const width = roomDiv.getAttribute("data-width") || '';
    const length = roomDiv.getAttribute("data-length") || '';

    const areas = [];
    roomDiv.querySelectorAll("tbody tr").forEach(row => {
      const areaName = row.querySelector("td input")?.value || row.querySelector("td")?.textContent.trim();
      const status = [...row.querySelectorAll('input[type="checkbox"]')]
        .filter(cb => cb.checked)
        .map(cb => cb.value)[0] || '';

      const commentInput = row.querySelector("textarea");
      const renter_comment = commentInput ? commentInput.value.trim() : "";

      areas.push({ areaName, status, renter_comment });
    });

    roomData.push({
      categoryName,
      width,
      length,
      areas,
      photo: photoFile
    });
    });

      //  Collect additional fields from inputs
    const extraInfo = {
      condition_report_date: document.getElementById('conditionReportDate')?.value || '',
      agreement_start_date: document.getElementById('agreementStartDate')?.value || '',
      renter_received_date: document.getElementById('renterReceivedDate')?.value || '',
      report_return_date: document.getElementById('reportReturnDate')?.value || '',
      address: document.getElementById('conditionAddress')?.value || '',
      full_name_1: document.getElementById('fullName1')?.value || '',
      agent_name: document.getElementById('agentName')?.value || '',
      agent_company_name: document.getElementById('agentCompanyName')?.value || '',
      renter_1: document.getElementById('renter1')?.value || '',
      renter_2: document.getElementById('renter2')?.value || ''
    };

      //  Combine room data and extra info
    const fullData = {
      extraInfo: extraInfo,
      rooms: roomData
    };

      //  Store the full JSON in hidden input
    const conditionDataInput = document.getElementById("conditionDataInput");
    conditionDataInput.value = JSON.stringify(fullData);

    console.log("Full Condition Report Data:", fullData);

    //  Optional: Close modal after saving
    closeModal("conditionModal");

    return roomData;
    }

                // Dynamically generate list of cards with the room data based from the listing from the Condition Report

          function createApplianceReportCard(room, roomIndex) {
            return `
              <div class="appliance-card" data-room-index="${roomIndex}">
                <div class="border border-blue-200 p-4 rounded-xl shadow-sm space-y-4 bg-gray-50">
                  <h3 class="text-md font-semibold text-blue-600">${room.categoryName} - Appliance Report</h3>
                  <div class="grid grid-cols-1 gap-3">
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600 text-left block">Windows Height</label>
                      <input type="text" placeholder="e.g. 15.68 sq. ft." class="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm" />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600 text-left block">Windows Length</label>
                      <input type="text" value="${room.length}" placeholder="e.g. 4.72 sq. ft." class="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm" />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600 text-left block">Windows Width</label>
                      <input type="text" value="${room.width}" placeholder="e.g. 3.90 sq. ft." class="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm" />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600 text-left block">Appliance Brand</label>
                      <input type="text" class="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm" />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600 text-left block">Model/Serial Number</label>
                      <input type="text" class="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm" />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600 text-left block">Location in Room</label>
                      <input type="text" class="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm" />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600 text-left block">Appliance Photo</label>
                      <input
                        type="file"
                        name="appliance_photo_${roomIndex}"
                        class="appliance-photo-input w-full px-3 py-2 rounded-xl border border-gray-300 text-sm"
                        data-preview-id="appliancePreview_${roomIndex}"
                      />
                      <img
                        id="appliancePreview_${roomIndex}"
                        class="mt-2 w-full h-auto rounded border border-gray-200 object-contain max-h-48"
                        style="display: none;"
                      />
                    </div>
                    <div class="flex flex-col">
                      <label class="text-sm font-medium text-gray-600">Comments</label>
                      <textarea class="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm resize-none"></textarea>
                    </div>
                  </div>
                </div>
              </div>
            `;
          }
      document.querySelector('.applianceReportBtn').addEventListener('click', function () {
      document.getElementById('applianceModal').classList.remove('hidden');

      function collectApplianceReports() {
        applianceReports = [];

        document.querySelectorAll('#applianceReportsContainer > div').forEach(card => {
        const inputs = card.querySelectorAll('input[type="text"]');
        const textarea = card.querySelector('textarea');

        applianceReports.push({
            roomName: card.querySelector('h3')?.textContent.split(' - ')[0].trim() || 'Unknown',
            window_height: inputs[0]?.value || '',
            window_length: inputs[1]?.value || '',
            window_width: inputs[2]?.value || '',
            brand: inputs[3]?.value || '',
            model_serial: inputs[4]?.value || '',
            location: inputs[5]?.value || '',
            comments: textarea?.value || ''
          });
        });

        console.log("Collected Appliance Reports:", applianceReports);

        const hiddenInput = document.getElementById('applianceReportsInput');
        if (hiddenInput) {
          hiddenInput.value = JSON.stringify(applianceReports);
        }
      }

      function attachApplianceListeners() {
          document.querySelectorAll('#applianceReportsContainer input, #applianceReportsContainer textarea')
            .forEach(input => {
              input.addEventListener('input', collectApplianceReports);
            });
      }


      document.querySelector('.applianceReportBtn').addEventListener('click', function () {
      document.getElementById('applianceModal').classList.remove('hidden');

      const rooms = collectRoomData(); // ← assume this function exists and works correctly
      console.log("Rooms Data:", rooms);

      const container = document.getElementById('applianceReportsContainer');
      container.innerHTML = '';

      if (!Array.isArray(rooms) || rooms.length === 0) {
        container.innerHTML = `<div class="text-center text-gray-500">No rooms added yet.</div>`;
        return;
      }

      rooms.forEach(room => {
        container.innerHTML += createApplianceReportCard(room);
      });

      attachApplianceListeners();
      collectApplianceReports();
      });

        const rooms = collectRoomData(); // collect room data
        console.log("Rooms Data:", rooms); //  log for debugging

        const container = document.getElementById('applianceReportsContainer');
        container.innerHTML = ''; // Clear container

        if (!Array.isArray(rooms) || rooms.length === 0) {
          container.innerHTML = `<div class="text-center text-gray-500">No rooms added yet.</div>`;
          return;
        }

        rooms.forEach(room => {
          container.innerHTML += createApplianceReportCard(room);
        });
      });

    function submitStandardReport() {
      const form = document.getElementById('registrationForm');

      const standardReport = {
        tenant_name: form.tenantName.value.trim(),
        audit_no: form.auditNo.value.trim(),
        auditor: form.auditor.value.trim(),
        inspection_address: form.inspectionAddress.value.trim(),
        managing_agent: form.agent.value.trim(),
        audit_date: form.auditDate.value,
        room: form.room.value.trim(),
        comments: form.comments.value.trim()
        // File will be handled in request.FILES
      };

      // Save JSON string to hidden input
      document.getElementById('standardReportDataInput').value = JSON.stringify(standardReport);
      console.log("Standard Report Data:", standardReport);

      }

    // Button to collect all Appliance Data
    function handleSaveApplianceReport() {
      applianceReports = [];

      document.querySelectorAll('#applianceReportsContainer > div').forEach(card => {
        const inputs = card.querySelectorAll('input[type="text"]');
        const textarea = card.querySelector('textarea');

        applianceReports.push({
          roomName: card.querySelector('h3')?.textContent.split(' - ')[0].trim() || 'Unknown',
          window_height: inputs[0]?.value || '',
          window_length: inputs[1]?.value || '',
          window_width: inputs[2]?.value || '',
          brand: inputs[3]?.value || '',
          model_serial: inputs[4]?.value || '',
          location: inputs[5]?.value || '',
          comments: textarea?.value || ''
        });
      });

      console.log("Collected Appliance Reports:", applianceReports);

      const hiddenInput = document.getElementById('applianceReportsInput');
      if (hiddenInput) {
        hiddenInput.value = JSON.stringify(applianceReports);
      }

      closeModal('applianceModal');
    }
    
    
    
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
        updateRoomListData();
    };

    const deleteBtn = document.createElement('button');
    deleteBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 hover:text-red-700" fill="none"
            viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M6 18L18 6M6 6l12 12"/>
        </svg>
    `;
    deleteBtn.onclick = () => {
        li.remove();
        updateRoomListData(); //
    };

      controls.appendChild(editBtn);
      controls.appendChild(deleteBtn);

      li.appendChild(span);
      li.appendChild(controls);

      return li;
    }

    function updateRoomListData() {
      const rooms = [];
      document.querySelectorAll('#roomList li span').forEach(span => {
          rooms.push(span.textContent);
      });
      document.getElementById('roomListData').value = JSON.stringify(rooms);
    }

    addRoomBtn.addEventListener('click', () => {
        const roomName = roomInput.value.trim();
        if (roomName) {
            roomList.appendChild(createRoomItem(roomName));
            roomInput.value = '';
            updateRoomListData();
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


    // Password strength validation
      const password = document.getElementById("password").value.trim();
      const passwordError = document.getElementById("passwordError");

      const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;

      if (!strongPasswordRegex.test(password)) {
        passwordError.textContent = "Password must be at least 8 characters long, include uppercase, lowercase, number, and special character.";
        passwordError.classList.remove("hidden");
        document.getElementById("password").classList.add("border-red-500");
      } else {
        passwordError.classList.add("hidden");
        document.getElementById("password").classList.remove("border-red-500");
      }


      // Password match validation
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
    document.getElementById('propertyImage').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('imagePreview');

    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    } else {
      preview.src = '';
    }
  });

  // This part will be about submitting the Registration Form data
    document.getElementById("registrationForm").addEventListener("submit", function (e) {

    e.preventDefault(); // Prevent default form submission

    // normally collect information about the data

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const nameInput = document.getElementById("name");
    const nameError = document.getElementById("nameError");

    // Empty field check
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
          // Now submit the form (with the hidden input included)
          e.target.submit();
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
    document.addEventListener("DOMContentLoaded", function () {
        const input = document.getElementById("propertyImage");
        const preview = document.getElementById("imagePreview");

        if (input && preview) {
          input.addEventListener("change", function (event) {
            const file = event.target.files[0];

            if (file && file.type.startsWith("image/")) {
              const reader = new FileReader();
              reader.onload = function (e) {
                preview.src = e.target.result;
              };
              reader.readAsDataURL(file);
            } else {
              preview.src = "";
            }
          });
        }
      });



    document.addEventListener("change", function (e) {
      const input = e.target;
      if (
        input.classList.contains("appliance-photo-input") ||
        input.classList.contains("room-photo-input")
      ) {
        const previewId = input.getAttribute("data-preview-id");
        const preview = document.getElementById(previewId);
        const file = input.files[0];

        if (file && preview) {
          const reader = new FileReader();
          reader.onload = function (event) {
            preview.src = event.target.result;
            preview.style.display = "block";
          };
          reader.readAsDataURL(file);
        } else if (preview) {
          preview.src = "";
          preview.style.display = "none";
        }
      }
    });


    document.addEventListener("change", function (e) {
      const input = e.target;
      if (
        input.classList.contains("room-photo-input") ||
        input.classList.contains("appliance-photo-input")
      ) {
        const previewId = input.getAttribute("data-preview-id");
        const preview = document.getElementById(previewId);
        const file = input.files[0];

        if (file && preview) {
          const reader = new FileReader();
          reader.onload = function (event) {
            preview.src = event.target.result;
            preview.style.display = "block";
          };
          reader.readAsDataURL(file);
        } else if (preview) {
          preview.src = "";
          preview.style.display = "none";
        }
      }
    });
document.addEventListener("DOMContentLoaded", function () {
  const addBtn = document.getElementById("addRoomAreaBtn");
  const tableBody = document.querySelector("#roomAreaTable tbody");

  if (addBtn && tableBody) {
    addBtn.addEventListener("click", function () {
      const newRow = document.createElement("tr");
      newRow.innerHTML = `
        <td><input type="text" placeholder="Area Name" class="border px-2 py-1 rounded" /></td>
        <td>
          <label><input type="checkbox" value="Clean" /> Clean</label>
          <label><input type="checkbox" value="Damaged" /> Damaged</label>
          <label><input type="checkbox" value="Needs Repair" /> Needs Repair</label>
        </td>
        <td><textarea class="border px-2 py-1 rounded w-full" placeholder="Comments"></textarea></td>
      `;
      tableBody.appendChild(newRow);
    });
  }
});

//   Validaton for number of floor Count
  function validateFloorCount(input) {
    const value = parseInt(input.value);
    if (isNaN(value) || value < 1) {
      alert("Floor Count must be at least 1.");
      input.value = ""; // Clear the invalid input
      input.focus();    // Bring focus back to the input
    }
  }

//
    function validateImageFile(input) {
      const file = input.files[0];
      if (file && !file.type.startsWith('image/')) {
        alert("Please upload a valid image file only (e.g. JPG, PNG).");
      input.value = ""; // clear the invalid file
    }
}


    function validateFileType(input) {
      const allowedExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx'];
      const errorMsg = document.getElementById('fileTypeError');

      if (!input.files.length) return;

      const fileName = input.files[0].name;
      const fileExtension = fileName.split('.').pop().toLowerCase();

      if (!allowedExtensions.includes(fileExtension)) {
        input.value = ''; // Clear the selected file
        errorMsg.classList.remove('hidden');
      } else {
        errorMsg.classList.add('hidden');
      }
    }




    // document.getElementById("roomCount").addEventListener("input", handleRoomCountChange);

    // function handleRoomCountChange() {
    //   const roomCount = parseInt(document.getElementById("roomCount").value);
    //   const roomContainer = document.getElementById("roomContainer");

    //   // Clear current room blocks
    //   roomContainer.innerHTML = "";

    //   if (!isNaN(roomCount) && roomCount > 0) {
    //     // Dynamically create room categories like Room 1, Room 2, etc.
    //     for (let i = 1; i <= roomCount; i++) {
    //       const categoryName = `Room ${i}`;
    //       categories.push(categoryName);
    //       addRoomBlock(categoryName);
    //     }

    //     populateCategoryDropdown(); // Refresh dropdown with new rooms
    //   }
    // }


