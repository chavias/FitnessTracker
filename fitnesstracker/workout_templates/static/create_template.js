let draggedItem = null;


function allowDrop(event) {
    event.preventDefault();
}


function drag(event) {
    draggedItem = event.target;
}


function drop(event) {
    event.preventDefault();
    const targetItem = event.target.closest('.exercise-row');
    if (targetItem && draggedItem !== targetItem) {
        
        const parent = draggedItem.parentNode;
        parent.insertBefore(draggedItem, targetItem.nextSibling);

        updateIndices();
    }
}


function updateIndices() {
    const exerciseRows = document.querySelectorAll('.exercise-row');
    exerciseRows.forEach((row, index) => {
        const inputField = row.querySelector('input[name^="exercises"]');
        const newName = `exercises-${index}-exercise_name`;
        inputField.setAttribute('name', newName);
    });
}


function removeExerciseRow(button) {
    const row = button.parentElement;
    row.remove();
    updateIndices();
}


function addExerciseRow() {
    const exerciseList = document.getElementById('exercise-list');
    const newIndex = exerciseList.children.length;

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

