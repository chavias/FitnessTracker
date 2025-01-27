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
                const parent = inputField.closest('.exercise-row');
                const detailsList = parent.querySelector('.details-list');

                if (applyToDetails && data.details) {
                    const existingRows = detailsList.children.length;

                    data.details.forEach((detail, index) => {
                        if (index < existingRows) {
                            const detailRow = detailsList.children[index];
                            detailRow.querySelector('input[name="repetitions[]"]').value = detail.repetitions;
                            detailRow.querySelector('input[name="weight[]"]').value = detail.weight;
                        } else {
                            addDetailRow(detailsList, detail.repetitions, detail.weight, false);
                        }
                    });
                }
            })
            .catch(error => console.error('Error loading last session:', error));
    }
}


function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    return csrfInput ? csrfInput.value : null;
}



function addDetailRow(detailsList, exerciseIndex) {
    const newDetailIndex = detailsList.children.length;

    const detailRow = document.createElement("div");
    detailRow.classList.add("detail-row");

    detailRow.innerHTML = `
            <input type="hidden" name="exercises-${exerciseIndex}-details-${newDetailIndex}-csrf_token" value="${getCsrfToken()}">
            <input type="number" name="exercises-${exerciseIndex}-details-${newDetailIndex}-repetitions" placeholder="Reps" required>
            <input type="number" name="exercises-${exerciseIndex}-details-${newDetailIndex}-weight" placeholder="Weight" step="0.5" required>
            <button type="button" onclick="removeDetailRow(this)">&#10006;</button>
    `;

    detailsList.appendChild(detailRow);
}


function addExerciseRow() {
    const exerciseList = document.getElementById("exercise-list");
    const newExerciseIndex = exerciseList.children.length;

    const exerciseRow = document.createElement("div");
    exerciseRow.classList.add("exercise-row");

    exerciseRow.innerHTML = `
        <input type="text" name="exercises-${newExerciseIndex}-name" placeholder="Exercise Name" required>
        <div class="details-list">
            <div class="detail-row">
            <input type="number" name="exercises-${newExerciseIndex}-details-0-repetitions" placeholder="Reps" required>
            <input type="number" name="exercises-${newExerciseIndex}-details-0-weight" placeholder="Weight" step="0.5" required>
            <button type="button" onclick="removeDetailRow(this)">&#10006;</button>
            <input type="hidden" name="exercises-${newExerciseIndex}-csrf_token" value="${getCsrfToken()}">
            <input type="hidden" name="exercises-${newExerciseIndex}-details-0-csrf_token" value="${getCsrfToken()}">
        </div>
        </div>
        <button type="button" onclick="addDetailRow(this.closest('.exercise-row').querySelector('.details-list'), ${newExerciseIndex})">Add Detail</button>
    `;

    exerciseList.appendChild(exerciseRow);
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
    exerciseList.innerHTML = '';

    if (templateId) {
        fetch(`/get_template/${templateId}`)
            .then(response => response.json())
            .then(data => {
                if (data.exercises) {
                    data.exercises.forEach(exercise => {
                        addExerciseRow(exercise.exercise, exercise.details);
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