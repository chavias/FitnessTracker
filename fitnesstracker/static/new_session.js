let draggedItem = null;

function enableSwipeToRemove() {
    const exerciseRows = document.querySelectorAll('.exercise-row:not(.swipe-enabled)'); // Only rows not initialized

    exerciseRows.forEach(row => {
        let startX = 0;
        let endX = 0;
        let startY = 0;
        let endY = 0;

        // Mark the row as initialized
        row.classList.add('swipe-enabled');

        row.addEventListener('touchstart', (event) => {
            // Capture starting X and Y positions
            startX = event.touches[0].clientX;
            startY = event.touches[0].clientY;
        });

        row.addEventListener('touchmove', (event) => {
            // Capture ending X and Y positions during movement
            endX = event.touches[0].clientX;
            endY = event.touches[0].clientY;
        });

        row.addEventListener('touchend', () => {
            // Calculate swipe distances
            const deltaX = startX - endX;
            const deltaY = Math.abs(startY - endY);

            // Trigger swipe-left only if horizontal swipe is significant and vertical movement is minimal
            if (deltaX > 50 && deltaY < 20) { // Adjust these thresholds as needed
                row.classList.add('swipe-left'); // Optional: Add animation class
                setTimeout(() => row.remove(), 300); // Remove row after animation
            }
        });
    });
}


function validateForm() {
    const exercises = document.querySelectorAll('.exercise-row');
    if (exercises.length === 0) {
        alert('Please add at least one exercise.');
        return false;
    }
    for (const exercise of exercises) {
        const name = exercise.querySelector('input[name="exercise[]"]').value.trim();
        if (!name) {
            alert('Exercise name cannot be empty.');
            return false;
        }
    }
    return true;
}


window.onload = function () {
    const dateField = document.getElementById("date");
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    dateField.value = formattedDate;
};


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



function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    return csrfInput ? csrfInput.value : null;
}


function addExerciseRow(exerciseName = '', details = [], exerciseIndex = 0) {
    const exerciseList = document.getElementById("exercise-list");
    const newExerciseIndex = exerciseIndex || exerciseList.children.length;

    const exerciseRow = document.createElement("div");
    exerciseRow.classList.add("exercise-row");

    exerciseRow.innerHTML = `
        <input type="text" name="exercises-${newExerciseIndex}-name" placeholder="Exercise Name" value="${exerciseName}" required>
        <div class="details-list">
            ${details.map((detail, detailIndex) => `
                <div class="detail-row">
                    <input type="number" name="exercises-${newExerciseIndex}-details-${detailIndex}-repetitions" placeholder="Reps" value="${detail.repetitions}" required>
                    <input type="number" name="exercises-${newExerciseIndex}-details-${detailIndex}-weight" placeholder="Weight" value="${detail.weight}" step="0.5" required>
                    <button type="button" onclick="removeDetailRow(this)">&#10006;</button>
                    <input type="hidden" name="exercises-${newExerciseIndex}-csrf_token" value="${getCsrfToken()}">
                    <input type="hidden" name="exercises-${newExerciseIndex}-details-${detailIndex}-csrf_token" value="${getCsrfToken()}">
                </div>
            `).join('')}
        </div>
        <button type="button" onclick="addDetailRow(this.closest('.exercise-row').querySelector('.details-list'), ${newExerciseIndex}, true)">Add Detail</button>
    `;

    exerciseList.appendChild(exerciseRow);
}


function addDetailRow(detailsList, exerciseIndex, triggerAutocomplete = true) {
    const newDetailIndex = detailsList.children.length;

    const detailRow = document.createElement("div");
    detailRow.classList.add("detail-row");

    detailRow.innerHTML = `
        <input type="number" name="exercises-${exerciseIndex}-details-${newDetailIndex}-repetitions" placeholder="Reps" required>
        <input type="number" name="exercises-${exerciseIndex}-details-${newDetailIndex}-weight" placeholder="Weight" step="0.5" required>
        <button type="button" onclick="removeDetailRow(this)">&#10006;</button>
        <input type="hidden" name="exercises-${exerciseIndex}-csrf_token" value="${getCsrfToken()}">
        <input type="hidden" name="exercises-${exerciseIndex}-details-${newDetailIndex}-csrf_token" value="${getCsrfToken()}">
    `;

    detailsList.appendChild(detailRow);

    // Trigger autocomplete if needed
    if (triggerAutocomplete) {
        const exerciseNameField = detailsList.closest('.exercise-row').querySelector('input[name="exercises-' + exerciseIndex + '-name"]');
    
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
}


function removeDetailRow(button) {
    button.closest('.detail-row').remove();
}


function removeDetailRow(button) {
    button.parentElement.remove();
}


function removeExerciseRow(button) {
    button.parentElement.remove();
}


function loadTemplate(templateId) {
    const exerciseList = document.getElementById('exercise-list');
    exerciseList.innerHTML = ''; // Clear the existing list

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


function allowDrop(event) {
    event.preventDefault();
}


function drag(event) {
    draggedItem = event.target;
    event.dataTransfer.setData("text", draggedItem.id);
}


function drop(event) {
    event.preventDefault();
    const targetItem = event.target.closest('.exercise-row');
    if (targetItem && draggedItem !== targetItem) {
        const parent = draggedItem.parentNode;
        parent.insertBefore(draggedItem, targetItem.nextSibling);
    }
}