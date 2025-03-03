let draggedItem = null;

// Update the name attributes for exercise and detail rows
function updateExerciseIndexes() {
    const exerciseRows = document.querySelectorAll('.exercise-row');
    exerciseRows.forEach((row, rowIndex) => {
        // Update exercise name
        const exerciseNameInput = row.querySelector('input[name^="exercises-"]');
        if (exerciseNameInput) {
            exerciseNameInput.setAttribute('name', `exercises-${rowIndex}-exercise_name`);
        }

        // Update details
        const detailRows = row.querySelectorAll('.detail-row');
        detailRows.forEach((detailRow, detailIndex) => {
            // Update repetitions, weight, and csrf_token fields
            const repetitionsInput = detailRow.querySelector('input[name^="exercises-"][name*="-repetitions"]');
            const weightInput = detailRow.querySelector('input[name^="exercises-"][name*="-weight"]');
            const csrfTokenInput = detailRow.querySelector('input[name^="exercises-"][name*="-csrf_token"]');

            if (repetitionsInput) {
                repetitionsInput.setAttribute('name', `exercises-${rowIndex}-details-${detailIndex}-repetitions`);
            }
            if (weightInput) {
                weightInput.setAttribute('name', `exercises-${rowIndex}-details-${detailIndex}-weight`);
            }
            if (csrfTokenInput) {
                csrfTokenInput.setAttribute('name', `exercises-${rowIndex}-details-${detailIndex}-csrf_token`);
            }
        });
    });
}

// Enable drag-and-drop functionality
function enableDragAndDrop() {
    const exerciseRows = document.querySelectorAll('.exercise-row:not(.drag-enabled)');

    exerciseRows.forEach(row => {
        row.classList.add('drag-enabled');
        row.setAttribute('draggable', 'true');

        row.addEventListener('dragstart', drag);
        row.addEventListener('dragover', allowDrop);
        row.addEventListener('drop', drop);
    });
}

// Drag-and-Drop handlers
function allowDrop(event) {
    event.preventDefault();
}

function drag(event) {
    draggedItem = event.target.closest('.exercise-row');
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', draggedItem.id);
}

function drop(event) {
    event.preventDefault();
    const targetItem = event.target.closest('.exercise-row');
    if (targetItem && draggedItem && draggedItem !== targetItem) {
        const parent = targetItem.parentNode;
        parent.insertBefore(draggedItem, targetItem.nextSibling);

        updateExerciseIndexes();
    }
}

function enableSwipeToRemove() {
    const exerciseRows = document.querySelectorAll('.exercise-row:not(.swipe-enabled)'); // Only rows not initialized

    exerciseRows.forEach(row => {
        let startX = 0;
        let startY = 0;
        let isDragging = false; // To differentiate between drag and swipe

        // Mark the row as initialized
        row.classList.add('swipe-enabled');

        row.addEventListener('touchstart', (event) => {
            startX = event.touches[0].clientX;
            startY = event.touches[0].clientY;
            isDragging = false; // Reset drag state
        });

        row.addEventListener('touchmove', (event) => {
            const currentX = event.touches[0].clientX;
            const currentY = event.touches[0].clientY;

            // Determine if movement is primarily horizontal
            if (Math.abs(currentX - startX) > Math.abs(currentY - startY)) {
                event.preventDefault(); // Prevent vertical scrolling
                isDragging = true; // Mark as dragging
            }
        });

        row.addEventListener('touchend', () => {
            if (!isDragging) return; // Ignore if no swipe occurred

            const deltaX = startX - event.changedTouches[0].clientX;

            // Trigger swipe-left if the horizontal swipe distance exceeds the threshold
            if (deltaX > 50) {
                row.classList.add('swipe-left'); // Optional: Add animation class
                setTimeout(() => row.remove(), 300); // Remove row after animation
            }
        });
    });
}

function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    return csrfInput ? csrfInput.value : null;
}



// Add a new exercise row
function addExerciseRow() {
    const exerciseList = document.getElementById('exercise-list');
    const newRow = document.createElement('div');
    newRow.classList.add('exercise-row');

    // Add HTML structure for the new exercise row
    newRow.innerHTML = `
        <input type="text" name="exercises-${exerciseList.children.length}-exercise_name" 
               placeholder="Exercise Name" required>
        <input type="hidden" name="exercises-${exerciseList.children.length}-csrf_token" value="${getCsrfToken()}">
        <div class="details-list"></div>
        <button type="button" onclick="addDetailRow(this.closest('.exercise-row').querySelector('.details-list'), ${exerciseList.children.length}, true)">
            &#x2795;
        </button>
    `;

    exerciseList.appendChild(newRow);

    // Re-initialize functionality for drag-and-drop and swipe-to-remove
    enableDragAndDrop();
    enableSwipeToRemove();
}

// Add a new detail row
function addDetailRow(detailsList, exerciseIndex) {
    const newDetailRow = document.createElement('div');
    newDetailRow.classList.add('detail-row');

    newDetailRow.innerHTML = `
        <input type="hidden" name="exercises-${exerciseIndex}-details-${detailsList.children.length}-csrf_token" value="${getCsrfToken()}">
        <input type="number" name="exercises-${exerciseIndex}-details-${detailsList.children.length}-repetitions" 
               placeholder="R" style="width: 35%" required>
        <input type="number" name="exercises-${exerciseIndex}-details-${detailsList.children.length}-weight" 
               placeholder="W" style="width: 35%" step="0.5" required>
        <button type="button" onclick="removeDetailRow(this)">&#10006;</button>
    `;

    detailsList.appendChild(newDetailRow);

    // Re-index the details for the current exercise row
    updateExerciseIndexes();
}

// Remove a detail row
function removeDetailRow(button) {
    const detailRow = button.closest('.detail-row');
    detailRow.remove();

    // Re-index the details for the current exercise row
    updateExerciseIndexes();
}

// Initialize the page
window.onload = function () {
    const dateField = document.getElementById("date");
    const today = new Date();
    dateField.value = today.toISOString().split('T')[0];

    // Initialize drag-and-drop and swipe-to-remove
    enableDragAndDrop();
    enableSwipeToRemove();
};

// Observer for dynamically added rows
const observer = new MutationObserver(() => {
    enableDragAndDrop();
    enableSwipeToRemove();
});

observer.observe(document.getElementById('exercise-list'), { childList: true });