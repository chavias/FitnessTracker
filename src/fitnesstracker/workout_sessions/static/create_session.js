let draggedItem = null;

function enableSwipeToRemove() {
    const exerciseRows = document.querySelectorAll('.exercise-row:not(.swipe-enabled)');

    exerciseRows.forEach(row => {
        let startX = 0;
        let startY = 0;
        let isDragging = false;

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
                row.classList.add('swipe-left');
                setTimeout(() => row.remove(), 300); // Remove row after animation
            }
        });
    });
}


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


function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    return csrfInput ? csrfInput.value : null;
}


function updateExerciseIndexes() {
    const exerciseRows = document.querySelectorAll('.exercise-row');

    exerciseRows.forEach((row, rowIndex) => {
        // Update exercise name input
        const nameInput = row.querySelector('input[type="text"]');
        if (nameInput) nameInput.name = `exercises-${rowIndex}-exercise_name`;

        // Update exercise CSRF token
        const csrfInput = row.querySelector('input[type="hidden"]');
        if (csrfInput) csrfInput.name = `exercises-${rowIndex}-csrf_token`;

        // Update detail rows
        const details = row.querySelectorAll('.detail-row');
        details.forEach((detail, detailIndex) => {
            const inputs = detail.querySelectorAll('input');
            if (inputs[0]) inputs[0].name = `exercises-${rowIndex}-details-${detailIndex}-repetitions`;
            if (inputs[1]) inputs[1].name = `exercises-${rowIndex}-details-${detailIndex}-weight`;
            if (inputs[2]) inputs[2].name = `exercises-${rowIndex}-details-${detailIndex}-csrf_token`; 
        });
    });
}

function addExerciseRow(exerciseName = '') {
    const exerciseList = document.getElementById('exercise-list');
    const newRow = document.createElement('div');
    newRow.classList.add('exercise-row');

    // Create inputs with initial name attributes
    newRow.innerHTML = `
        <input type="text" placeholder="Exercise Name" value="${exerciseName}" required>
        <input type="hidden" value="${getCsrfToken()}">
        <div class="details-list"></div>
        <div>
        <button type="button" onclick="addDetailRow(this)"  style="color: black;" >
            <span class="material-symbols-outlined">
            add
            </span> 
        </button>
        </div>
    `;

    exerciseList.appendChild(newRow);
    updateExerciseIndexes(); // Update names immediately
    enableDragAndDrop();
    enableSwipeToRemove();
}


function addDetailRow(button, triggerAutocomplete = true) {
    const exerciseRow = button.closest('.exercise-row');
    const detailsList = exerciseRow.querySelector('.details-list');
    
    // Create new detail row
    const newRow = document.createElement('div');
    newRow.className = 'detail-row';
    newRow.innerHTML = `
    <input type="number" placeholder="R" style="width: 35%" required>
    <input type="number" placeholder="W" step="0.5" style="width: 35%" required>
    <input type="hidden" value="${getCsrfToken()}">
    <button type="button" onclick="removeDetailRow(this)" style="color: black;">
        <span class="material-symbols-outlined">delete</span>
    </button>
    `;

    detailsList.appendChild(newRow);
    updateExerciseIndexes();

    // Autocomplete handling
    if (triggerAutocomplete) {
        const exerciseName = exerciseRow.querySelector('input[type="text"]').value;
        if (exerciseName) {
            const detailIndex = detailsList.children.length - 1;
            fetch(`/get_last_session/${exerciseName}`)
                .then(response => response.json())
                .then(data => {
                    if (data.details[detailIndex]) {
                        newRow.querySelector('input:nth-of-type(1)').value = data.details[detailIndex].repetitions;
                        newRow.querySelector('input:nth-of-type(2)').value = data.details[detailIndex].weight;
                    }
                });
        }
    }
}


function removeDetailRow(button) {
    const detailRow = button.closest('.detail-row');
    detailRow.remove();

    updateExerciseIndexes();
}


window.onload = function () {
    const dateField = document.getElementById("date");

    // Only set today's date if the field is empty
    if (!dateField.value) {
        const today = new Date();
        dateField.value = today.toISOString().split('T')[0];
    }

    enableDragAndDrop();
    enableSwipeToRemove();
};


const observer = new MutationObserver(() => {
    enableDragAndDrop();
    enableSwipeToRemove();
});

observer.observe(document.getElementById('exercise-list'), { childList: true });


function loadLastSession(inputField) {
    const exerciseRow = inputField.closest('.exercise-row');
    const exerciseList = document.getElementById('exercise-list');
    const rowIndex = Array.from(exerciseList.children).indexOf(exerciseRow);
    
    fetch(`/get_last_session/${inputField.value.trim()}`)
        .then(response => response.json())
        .then(data => {
            const detailsList = exerciseRow.querySelector('.details-list');
            detailsList.innerHTML = ''; // Clear existing details

            data.details.forEach((detail, i) => {
                const button = exerciseRow.querySelector('button');
                addDetailRow(button, false); // Add without autocomplete trigger
                
                const newRow = detailsList.lastElementChild;
                newRow.querySelector('input:nth-of-type(1)').value = detail.repetitions;
                newRow.querySelector('input:nth-of-type(2)').value = detail.weight;
            });
            updateExerciseIndexes();
        });
}


function loadTemplate(templateId) {
    const exerciseList = document.getElementById('exercise-list');
    exerciseList.innerHTML = '';

    if (templateId) {
        fetch(`/get_template/${templateId}`)
            .then(response => response.json())
            .then(data => {
                if (data.exercises) {
                    data.exercises.forEach((exercise, index) => {
                        addExerciseRow(exercise.exercise, exercise.details, index);
                    });
                }
            })
            .catch(error => console.error('Error fetching template:', error));
    }
}


function validateForm(event) {
    const templateSelect = document.getElementById('template');
    const warningDiv = document.getElementById('template-warning');
    
    if (!templateSelect.value) {
        event.preventDefault(); // Prevent form submission
        warningDiv.style.display = 'block';
        
        // Scroll to warning
        warningDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Hide warning after 5 seconds
        setTimeout(() => {
            warningDiv.style.display = 'none';
        }, 5000);
        
        return false;
    }
    
    return true;
}