// Set default categories here that will be displayed by default, will change soon based on 
    let categories = ['Lounge Room', 'Kitchen', 'Bedroom'];

    function populateCategoryDropdown() {
      const select = document.getElementById("modalRoomCategory");
      select.innerHTML = '';
      categories.forEach(cat => {
        const option = document.createElement("option");
        option.value = cat;
        option.textContent = cat;
        select.appendChild(option);
      });
    }

    function addRoomBlock(categoryName) {
      const roomContainer = document.getElementById("roomContainer");

      const roomDiv = document.createElement("div");
      roomDiv.className = "mb-6 border rounded-md p-4";

      roomDiv.innerHTML = `
        <div class="flex justify-between items-center mb-2">
          <h3 class="font-semibold text-lg category-name">${categoryName}</h3>
          <div class="flex gap-2">
            <button class="text-blue-500" type="button" onclick="openEditModal(this)" data-category="${categoryName}">
            <i class="fas fa-edit"></i>
          </button>
            <button class="text-red-500" type="button" onclick="deleteRoomBlock(this)"><i class="fas fa-trash"></i></button>
          </div>
        </div>

        <table class="w-full text-center border border-blue-500">
          <thead class="bg-blue-500 text-white">
            <tr>
              <th class="py-2">Room area</th>
              <th>Clean</th>
              <th>Undamaged</th>
              <th>Working</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-t">
              <td class="py-2">Walls</td>
              <td><input type="checkbox" name="Walls" value="Clean" onclick="checkOnlyOne(this)"></td>
              <td><input type="checkbox" name="Walls" value="Undamaged" onclick="checkOnlyOne(this)"></td>
              <td><input type="checkbox" name="Walls" value="Working" onclick="checkOnlyOne(this)"></td>
            </tr>
          </tbody>
        </table>

        <button type="button" onclick="addNewRoomArea(this)" class="mt-3 text-sm text-blue-600 hover:underline">Add new room area</button>
      `;

      roomContainer.appendChild(roomDiv);
    }


    function addNewCategory() {
      document.getElementById("newCategoryInput").value = "";
      document.getElementById("addCategoryModal").classList.remove("hidden");
    }
    
    function addNewRoomArea(button) {
      const table = button.previousElementSibling.querySelector("tbody");
      const newRow = document.createElement("tr");
      newRow.className = "border-t";
      newRow.innerHTML = `
        <td class="py-2"><input type="text" placeholder="New area" class="border px-2 py-1 rounded w-4/5 mx-auto text-center" /></td>
        <td><input type="checkbox" onclick="checkOnlyOne(this)"></td>
        <td><input type="checkbox" onclick="checkOnlyOne(this)"></td>
        <td><input type="checkbox" onclick="checkOnlyOne(this)"></td>
      `;
      table.appendChild(newRow);
    }

    function confirmAddCategory() {
      const input = document.getElementById("newCategoryInput").value.trim();
      if (input === "") return alert("Category name cannot be empty.");
      if (categories.includes(input)) return alert("Category already exists.");

      categories.push(input);
      populateCategoryDropdown();
      document.getElementById('modalRoomCategory').value = input;
      addRoomBlock(input);
      closeAddCategoryModal();
    }

    function closeAddCategoryModal() {
      document.getElementById("addCategoryModal").classList.add("hidden");
    }

    function checkOnlyOne(checkbox) {
      const row = checkbox.parentElement.parentElement;
      const checkboxes = row.querySelectorAll('input[type="checkbox"]');
      checkboxes.forEach(cb => {
        if (cb !== checkbox) cb.checked = false;
      });
    }

    // function to close the Edit Category Modal
    function closeEditModal() {
      document.getElementById("editCategoryModal").classList.add("hidden");
      currentEditingRoomDiv = null;
    }
    // Init on load
    document.addEventListener("DOMContentLoaded", () => {
      populateCategoryDropdown();
      categories.forEach(cat => addRoomBlock(cat));
    });

    // Edit category Name here
    function editCategoryName(button) {
      const roomBlock = button.closest("div.mb-6");
      const heading = roomBlock.querySelector(".category-name");

      const currentName = heading.textContent;
      const input = document.createElement("input");
      input.type = "text";
      input.value = currentName;
      input.className = "border px-2 py-1 rounded w-full";

      heading.replaceWith(input);
      input.focus();

      input.addEventListener("blur", () => saveEditedCategoryName(input, roomBlock, currentName));
      input.addEventListener("keydown", e => {
        if (e.key === "Enter") input.blur();
      });
    }

  function saveEditedCategoryName(input, roomBlock, oldName) {
    const newName = input.value.trim();
    if (!newName) {
      alert("Category name cannot be empty.");
      input.focus();
      return;
    }

    // Prevent duplicates
    if (categories.includes(newName) && newName !== oldName) {
      alert("Category name already exists.");
      input.focus();
      return;
    }

  // Update the categories array
  const index = categories.indexOf(oldName);
  if (index !== -1) categories[index] = newName;

  // Replace input with heading again
  const newHeading = document.createElement("h3");
  newHeading.className = "font-semibold text-lg category-name";
  newHeading.textContent = newName;
  input.replaceWith(newHeading);

  // Update dropdown
  populateCategoryDropdown();
}
    
function openEditModal(button) {
  const roomDiv = button.closest("div.mb-6");
  const categoryName = roomDiv.querySelector(".category-name").textContent;

  console.log("Opening Edit Modal for:", categoryName);

  // Set room name input
  document.getElementById("editCategoryInput").value = categoryName;

  // Set width/length (optional)
  const width = roomDiv.getAttribute("data-width") || "";
  const length = roomDiv.getAttribute("data-length") || "";

  console.log("Room dimensions - Width:", width, "Length:", length);

  document.getElementById("roomWidth").value = width;
  document.getElementById("roomLength").value = length;

  // Populate and select current category
  populateCategoryDropdown(categoryName);

  // Clone the table from roomDiv and inject into modal
  const originalTable = roomDiv.querySelector("table").cloneNode(true);
  originalTable.id = "editRoomAreaTable";

  // Also change checkbox onclick to work inside modal (optional: you can leave them the same if it's global)
  const tableWrapper = document.getElementById("editRoomAreaTableWrapper");
  tableWrapper.innerHTML = ""; // Clear previous
  tableWrapper.appendChild(originalTable);

  // Log all rows and checkbox status
  const rows = originalTable.querySelectorAll("tbody tr");
  rows.forEach(row => {
    const area = row.querySelector("td input") ? row.querySelector("td input").value : row.querySelector("td").textContent;
    const checkboxes = row.querySelectorAll('input[type="checkbox"]');
    const status = Array.from(checkboxes).map(cb => ({
      checked: cb.checked,
      value: cb.value
    }));

    console.log(`Room Area: ${area}`, status);
  });

  // Show modal
  const modal = document.getElementById("editCategoryModal");
  modal.classList.remove("hidden");
  modal.setAttribute("data-room-div-id", roomDiv.dataset.id || "");
  modal.setAttribute("data-original-category", categoryName);
}

  function populateCategoryDropdown(selectedCategory = "") {
  const dropdown = document.getElementById("modalRoomCategory");
  dropdown.innerHTML = ""; // Clear current options

  categories.forEach(cat => {
    const option = document.createElement("option");
    option.value = cat;
    option.textContent = cat;
    if (cat === selectedCategory) option.selected = true;
    dropdown.appendChild(option);
  });
}

function saveEditedCategoryFromModal() {
  const modal = document.getElementById("editCategoryModal");

  const newName = document.getElementById("editCategoryInput").value.trim();
  const width = document.getElementById("roomWidth").value;
  const length = document.getElementById("roomLength").value;
  const selectedCategory = document.getElementById("modalRoomCategory").value;

  if (!newName) {
    alert("Room Name cannot be empty.");
    return;
  }

  const roomDiv = Array.from(document.querySelectorAll(".category-name"))
    .find(el => el.textContent === modal.getAttribute("data-original-category"))
    ?.closest(".mb-6");

  if (roomDiv) {
    // Update name and dimensions
    roomDiv.querySelector(".category-name").textContent = newName;
    roomDiv.setAttribute("data-width", width);
    roomDiv.setAttribute("data-length", length);
  }

  closeEditModal();
}



function collectRoomData() {
    const roomData = [];

    const roomBlocks = document.querySelectorAll("#roomContainer .mb-6");

    console.log("Found rooms: ", roomBlocks.length);

    roomBlocks.forEach(roomDiv => {
        const categoryNameElement = roomDiv.querySelector(".category-name");
        const categoryName = categoryNameElement ? categoryNameElement.textContent.trim() : "Unknown";

        const width = roomDiv.getAttribute("data-width") || '';
        const length = roomDiv.getAttribute("data-length") || '';

        const areas = [];

        roomDiv.querySelectorAll("tbody tr").forEach(row => {
            let areaName = "";

            const input = row.querySelector("td input[type='text']");
            if (input) {
                areaName = input.value.trim();
            } else {
                const cell = row.querySelector("td");
                if (cell) {
                    areaName = cell.textContent.trim();
                }
            }

            const checkboxes = row.querySelectorAll('input[type="checkbox"]');
            let status = '';
            checkboxes.forEach(cb => {
                if (cb.checked) status = cb.value;
            });

            areas.push({
                areaName: areaName,
                status: status
            });
        });

        roomData.push({
            categoryName: categoryName,
            width: width,
            length: length,
            areas: areas
        });
    });

    console.log("Final Room Data:", roomData);
}