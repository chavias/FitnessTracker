let draggedItem = null;

// Set the current date in the date field
window.onload = function () {
    const dateField = document.getElementById("date");
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    dateField.value = formattedDate;
};


// Add an exercise row with drag-and-drop support
function addExerciseRow(exercise) {
    const exerciseList = document.getElementById('exercise-list');
    const newRow = document.createElement('div');
    const rowId = 'exercise-row-' + Date.now();  // Create a unique ID for the row
    newRow.className = 'exercise-row'; // Add a class for styling
    newRow.id = rowId; // Assign unique ID
    newRow.setAttribute('draggable', 'true');
    newRow.setAttribute('ondragstart', 'drag(event)');
    newRow.setAttribute('ondragover', 'allowDrop(event)');
    newRow.setAttribute('ondrop', 'drop(event)');

    newRow.innerHTML = `
            <input type="text" name="exercise[]" style="width : 300%" value="${exercise || ''}" placeholder="Exercise Name" oninput="loadLastSession(this)" required>
            <input type="number" name="sets[]" style="width : 40%" placeholder="S" required>
            <input type="number" name="reps[]" style="width : 40%" placeholder="R" required>
            <input type="number" name="weight[]" style="width : 60%" placeholder="W" step="0.5" required>
            <button type="button" class="remove-button" onclick="removeExerciseRow(this)">&#10006;</button>
        `;

    // Append the new row to the exercise list
    exerciseList.appendChild(newRow);

    // Trigger the `loadLastSession` function immediately for autofill
    const exerciseInput = newRow.querySelector('input[name="exercise[]"]');
    if (exerciseInput.value) {
        loadLastSession(exerciseInput);
    }
}


function addExerciseRowWithoutTemplate() {
    const exerciseList = document.getElementById('exercise-list');
    const newRow = document.createElement('div');
    const rowId = 'exercise-row-' + Date.now();  // Create a unique ID for the row
    newRow.className = 'exercise-row'; // Add a class for styling
    newRow.id = rowId; // Assign unique ID
    newRow.setAttribute('draggable', 'true');
    newRow.setAttribute('ondragstart', 'drag(event)');
    newRow.setAttribute('ondragover', 'allowDrop(event)');
    newRow.setAttribute('ondrop', 'drop(event)');

    newRow.innerHTML = `
            <input type="text" name="exercise[]" style="width : 300%" placeholder="Exercise Name" oninput="loadLastSession(this)" required>
            <input type="number" name="sets[]" style="width : 40%" placeholder="S" required>
            <input type="number" name="reps[]" style="width : 40%" placeholder="R" required>
            <input type="number" name="weight[]" style="width : 60%" placeholder="W" step="0.5" required>
            <button type="button" class="remove-button" onclick="removeExerciseRow(this)">&#10006;</button>
        `;
    exerciseList.appendChild(newRow);
}

function removeExerciseRow(button) {
    button.parentElement.remove();
}

// Fetch template data when a template is selected
function loadTemplate(templateId) {
    const exerciseList = document.getElementById('exercise-list');
    exerciseList.innerHTML = ''; // Clear existing fields

    if (templateId) {
        fetch(`/get_template/${templateId}`)
            .then(response => response.json())
            .then(data => {
                if (data.exercises) {
                    data.exercises.forEach(exercise => {
                        addExerciseRow(
                            exercise.exercise,
                            exercise.default_sets,
                            exercise.default_reps,
                            exercise.default_weight
                        );
                    });
                }
            })
            .catch(error => console.error('Error fetching template:', error));
    }
}


function loadLastSession(inputField) {
    const exercise = inputField.value;
    if (exercise) {
        fetch(`/get_last_session/${exercise}`)
            .then(response => response.json())
            .then(data => {
                const parent = inputField.parentElement;
                parent.querySelector('input[name="sets[]"]').value = data.sets || '';
                parent.querySelector('input[name="reps[]"]').value = data.reps || '';
                parent.querySelector('input[name="weight[]"]').value = data.weight || '';
            });
    }
}


// Allow dropping an element
function allowDrop(event) {
    event.preventDefault();
}


// Handle the start of a drag event
function drag(event) {
    draggedItem = event.target;  // Store the dragged element
    event.dataTransfer.setData("text", draggedItem.id); // Set the ID for drag
}


// Handle the drop event to swap the elements
function drop(event) {
    event.preventDefault();
    const targetItem = event.target.closest('.exercise-row');
    if (targetItem && draggedItem !== targetItem) {
        // Swap the dragged item with the target item
        const parent = draggedItem.parentNode;
        parent.insertBefore(draggedItem, targetItem.nextSibling);

        // Reindex the rows after reordering
        updateIndices();
    }
}

// Update the indices of input names after reordering
function updateIndices() {
    const exerciseRows = document.querySelectorAll('.exercise-row');
    exerciseRows.forEach((row, index) => {
        row.querySelectorAll('input').forEach(input => {
            const name = input.name.split('[]')[0];
            input.name = `${name}[${index}]`;
        });
    });
}
