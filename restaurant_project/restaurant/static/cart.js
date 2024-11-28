document.addEventListener('DOMContentLoaded', function () {
    // Load the previously selected items and date from localStorage
    const selectedItems = JSON.parse(localStorage.getItem('selected_items')) || [];
    const savedDate = localStorage.getItem('selected_date') || '';

    const dateInput = document.getElementById('orderDate');

    // Apply the saved date to the date picker input field
    if (dateInput && savedDate) {
        dateInput.value = savedDate;
    }

    // Function to gray out selected items
    function grayOutSelectedItems(items) {
        items.forEach(itemId => {
            const checkbox = document.querySelector(`input[name="selected_items"][value="${itemId}"]`);
            if (checkbox) {
                checkbox.checked = true;
                checkbox.disabled = true;
                const row = checkbox.closest('tr');
                row.style.backgroundColor = '#f0f0f0'; // Gray out the selected item
                row.querySelector('input[name^="instruction_"]').disabled = true; // Disable the instruction input

                // Add click event listener on the row
                row.addEventListener('click', function (event) {
                    // Check if the click event is on a disabled checkbox
                    if (event.target.tagName === 'INPUT' && event.target.type === 'checkbox' && event.target.disabled) {
                        alert("You can't select this item for today.");
                    }
                });
            }
        });
    }

    // Mark the previously selected items
    grayOutSelectedItems(selectedItems);

    // Event listener for the date change
    if (dateInput) {
        dateInput.addEventListener('change', function () {
            const newDate = dateInput.value;

            // Check if the new date matches the saved date
            if (newDate === savedDate) {
                // Gray out the previously selected items again
                grayOutSelectedItems(selectedItems);
            } else {
                // Clear selected items from localStorage
                localStorage.removeItem('selected_items');
                localStorage.setItem('selected_date', newDate); // Store the new selected date

                // Enable all checkboxes again
                document.querySelectorAll('input[name="selected_items"]').forEach(checkbox => {
                    checkbox.disabled = false;
                    const row = checkbox.closest('tr');
                    row.style.backgroundColor = ''; // Reset the row color
                    row.querySelector('input[name^="instruction_"]').disabled = false; // Enable instruction input
                });
            }
        });
    }

    // Event listener for the Order Now button to store the selected items and date
    const orderButton = document.querySelector('button[type="submit"]');
    if (orderButton) {
        orderButton.addEventListener('click', function () {
            const selectedCheckboxes = document.querySelectorAll('input[name="selected_items"]:checked');
            const selectedIds = Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
            localStorage.setItem('selected_items', JSON.stringify(selectedIds));
            localStorage.setItem('selected_date', dateInput.value); // Save the selected date
        });
    }
});
