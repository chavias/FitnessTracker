    // Global variable to store the dragged element
    let draggedItem = null;

    // Allow the dragged item to be dropped
    function allowDrop(event) {
        event.preventDefault();
    }

    // Handle the start of a drag event
    function drag(event) {
        draggedItem = event.target;
    }

    // Handle the drop event to swap the elements
    function drop(event) {
        event.preventDefault();
        const targetItem = event.target.closest('.exercise-row');
        if (targetItem && draggedItem !== targetItem) {
            // Swap the dragged item with the target item
            const parent = draggedItem.parentNode;
            parent.insertBefore(draggedItem, targetItem.nextSibling);

            // Update the indices for the input fields after reordering
            updateIndices();
        }
    }

    // Update the indices for the input field names after reordering
    function updateIndices() {
        const exerciseRows = document.querySelectorAll('.exercise-row');
        exerciseRows.forEach((row, index) => {
            const inputField = row.querySelector('input[name^="exercises"]');
            const newName = `exercises-${index}-exercise_name`;
            inputField.setAttribute('name', newName);
        });
    }

    // Function to remove an exercise row
    function removeExerciseRow(button) {
        const row = button.parentElement;
        row.remove();
        updateIndices();  // Re-index the remaining fields after removal
    }

    // Function to add a new exercise row (for dynamic addition)
    function addExerciseRow() {
        const exerciseList = document.getElementById('exercise-list');
        const newIndex = exerciseList.children.length;

        // Create a new exercise row with input fields
        const newRow = document.createElement('div');
        newRow.classList.add('exercise-row');
        newRow.setAttribute('id', `exercise-${newIndex}`);
        newRow.setAttribute('draggable', 'true');
        newRow.setAttribute('ondragstart', 'drag(event)');
        newRow.setAttribute('ondragover', 'allowDrop(event)');
        newRow.setAttribute('ondrop', 'drop(event)');

        newRow.innerHTML = `
            <input type="text" name="exercises-${newIndex}-exercise_name" placeholder="Exercise Name" required>
            <button type="button" onclick="removeExerciseRow(this)">&#10006;</button>
        `;
        exerciseList.appendChild(newRow);
    }

