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
        const exerciseNameInput = row.querySelector('input[name^="exercises-"]');
        if (exerciseNameInput) {
            exerciseNameInput.setAttribute('name', `exercises-${rowIndex}-exercise_name`);
        }

        const detailRows = row.querySelectorAll('.detail-row');
        detailRows.forEach((detailRow, detailIndex) => {
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


function addExerciseRow(exerciseName='') {
    const exerciseList = document.getElementById('exercise-list');
    const newRow = document.createElement('div');
    newRow.classList.add('exercise-row');

    newRow.innerHTML = `
        <input type="text" name="exercises-${exerciseList.children.length}-exercise_name" value="${exerciseName}"
               placeholder="Exercise Name" required>
        <input type="hidden" name="exercises-${exerciseList.children.length}-csrf_token" value="${getCsrfToken()}">
        <div class="details-list"></div>
        <button type="button" onclick="addDetailRow(this.closest('.exercise-row').querySelector('.details-list'), ${exerciseList.children.length}, true)">
            &#x2795;
        </button>
    `;

    exerciseList.appendChild(newRow);

    enableDragAndDrop();
    enableSwipeToRemove();
}


function addDetailRow(detailsList, exerciseIndex, triggerAutocomplete = true) {
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

    if (triggerAutocomplete) {
        const exerciseNameField = detailsList.closest('.exercise-row').querySelector('input[name="exercises-' + exerciseIndex + '-exercise_name"]');
    
        if (exerciseNameField && exerciseNameField.value.trim()) {
            fetch(`/get_last_session/${exerciseNameField.value.trim()}`)
                .then(response => response.json())
                .then(data => {
                    const lastRow = detailsList.lastElementChild;
                    const lastDetail = data.details[detailsList.children.length - 1];

                    if (lastDetail) {
                        lastRow.querySelector(`input[name="exercises-${exerciseIndex}-details-${detailsList.children.length - 1}-repetitions"]`).value = lastDetail.repetitions;
                        lastRow.querySelector(`input[name="exercises-${exerciseIndex}-details-${detailsList.children.length - 1}-weight"]`).value = lastDetail.weight;
                    }
                })
                .catch(error => console.error('Error autocompleting last detail:', error));
        }
    }

    updateExerciseIndexes();
}


function removeDetailRow(button) {
    const detailRow = button.closest('.detail-row');
    detailRow.remove();

    updateExerciseIndexes();
}


window.onload = function () {
    const dateField = document.getElementById("date");
    const today = new Date();
    dateField.value = today.toISOString().split('T')[0];

    enableDragAndDrop();
    enableSwipeToRemove();
};

const observer = new MutationObserver(() => {
    enableDragAndDrop();
    enableSwipeToRemove();
});

observer.observe(document.getElementById('exercise-list'), { childList: true });

function loadLastSession(inputField, applyToDetails = false) {
    const exerciseName = inputField.value.trim();

    if (exerciseName) {
        fetch(`/get_last_session/${exerciseName}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);

                const parent = inputField.closest('.exercise-row');
                if (!parent) {
                    console.error('Could not find the parent exercise row');
                    return;
                }

                const detailsList = parent.querySelector('.details-list');
                if (!detailsList) {
                    console.error('Could not find details list');
                    return;
                }

                if (applyToDetails && data.details) {
                    const existingRows = detailsList.children.length;

                    // Iterate through the details and update or add new detail rows
                    data.details.forEach((detail, index) => {
                        const repetitionsInputName = `exercises-${parent.dataset.exerciseIndex}-details-${index}-repetitions`;
                        const weightInputName = `exercises-${parent.dataset.exerciseIndex}-details-${index}-weight`;

                        if (index < existingRows) {
                            const detailRow = detailsList.children[index];
                            const repetitionsInput = detailRow.querySelector(`input[name="${repetitionsInputName}"]`);
                            const weightInput = detailRow.querySelector(`input[name="${weightInputName}"]`);
                            
                            if (repetitionsInput && weightInput) {
                                repetitionsInput.value = detail.repetitions;
                                weightInput.value = detail.weight;
                            } else {
                                console.error(`Inputs not found for ${repetitionsInputName} and ${weightInputName}`);
                            }
                        } else {
                            addDetailRow(detailsList, parent.dataset.exerciseIndex, detail.repetitions, detail.weight);
                        }
                    });

                    // If there are more existing rows than the new session details, remove excess rows
                    for (let i = data.details.length; i < existingRows; i++) {
                        detailsList.children[i].remove();
                    }
                }
            })
            .catch(error => console.error('Error loading last session:', error));
    }
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


function refreshCsrfToken() {
    fetch('/refresh_csrf')
    .then(response => response.json())
    .then(data => {
        let csrfInput = document.querySelector("input[name='csrf_token']");
        if (csrfInput) {
            csrfInput.value = data.csrf_token;
        }
    });
}

// Refresh CSRF token every 10 minutes
setInterval(refreshCsrfToken, 10 * 60 * 1000);