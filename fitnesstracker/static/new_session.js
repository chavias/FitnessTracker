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


function addDetailRow(detailsList, repetitions = '', weight = '', triggerAutocomplete = true) {
    const detailRow = document.createElement('div');
    detailRow.className = 'detail-row';

    detailRow.innerHTML = `
        <input type="number" name="repetitions[]" style="width: 35%" placeholder="Reps" value="${repetitions}" required>
        <input type="number" name="weight[]" style="width: 35%" placeholder="Weight" value="${weight}" step="0.5" required>
        <button type="button" onclick="removeDetailRow(this)">&#10006;</button>`;

    detailsList.appendChild(detailRow);

    // Prevent touch events on the detail row from triggering parent events
    // detailRow.addEventListener('touchstart', (event) => event.stopPropagation());
    // detailRow.addEventListener('touchmove', (event) => event.stopPropagation());
    // detailRow.addEventListener('touchend', (event) => event.stopPropagation());

    if (triggerAutocomplete) {
        // Ensure only the last row is updated with data
        const exerciseNameField = detailsList.closest('.exercise-row').querySelector('input[name="exercise[]"]');
        if (exerciseNameField.value.trim()) {
            fetch(`/get_last_session/${exerciseNameField.value.trim()}`)
                .then(response => response.json())
                .then(data => {
                    const lastRow = detailsList.lastElementChild;
                    const detail = data.details[detailsList.children.length - 1];
                    if (detail) {
                        lastRow.querySelector('input[name="repetitions[]"]').value = detail.repetitions;
                        lastRow.querySelector('input[name="weight[]"]').value = detail.weight;
                        console.log('Completed details');
                    }
                    console.log(detail);
                })
                .catch(error => console.error('Error autocompleting last detail:', error));
        }
    }
}


function addExerciseRow(exercise = '', details = [], remove = false) {
    const exerciseList = document.getElementById('exercise-list');
    const newRow = document.createElement('div');
    const rowId = `exercise-row-${Date.now()}`;

    newRow.className = 'exercise-row';
    newRow.id = rowId;
    newRow.setAttribute('draggable', 'true');
    newRow.setAttribute('ondragstart', 'drag(event)');
    newRow.setAttribute('ondragover', 'allowDrop(event)');
    newRow.setAttribute('ondrop', 'drop(event)');

    newRow.innerHTML = `
        <input type="text" name="exercise[]" value="${exercise}" placeholder="Exercise Name" oninput="loadLastSession(this, true)" required>
        <div class="details-list">
            ${details.map(detail => `<div class='detail-row'>
                <input type="number" name="repetitions[]" style="width: 35%" value="${detail.repetitions}" placeholder="R" required>
                <input type="number" name="weight[]" style="width: 35%" value="${detail.weight}" placeholder="W" step="0.5" required>
                <button type="button" onclick="removeDetailRow(this)">&#10006;</button>
            </div>`).join('')}
        </div>
        <button type="button" onclick="addDetailRow(this.closest('.exercise-row').querySelector('.details-list'), '', '')">&#10010</button>
    `;
    console.log(exerciseList);
    exerciseList.appendChild(newRow);

    enableSwipeToRemove();
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
