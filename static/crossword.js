document.addEventListener('DOMContentLoaded', function() {
    const crosswordGrid = document.getElementById('crossword-grid');
    const acrossCluesList = document.getElementById('across-clues');
    const downCluesList = document.getElementById('down-clues');
    const crosswordContainer = document.getElementById('crossword-grid');
    let crosswordData = {};

    const customDialog = document.getElementById("customDialog");
    const customDialogContent = document.getElementById('customDialogContent');
    const customDialogHeader = document.getElementById('customDialogHeader');

    document.getElementById('generate').addEventListener('click', function(){
        generatePuzzle();
        resetGame();
    });
    document.getElementById('show-answers-button').addEventListener('click', showAnswers);
    document.getElementById('start-game-button').addEventListener('click', function() {
        resetGame();
        startTimer(); 
    });
    document.getElementById('submit-answers-button').addEventListener('click', function() {
        stopTimer();
        checkAnswers();
    });

    // Control the hit Dialog
    document.getElementById('hint-button').addEventListener('click', showHint);
    document.getElementById('MoreHintButton').addEventListener('click', showMoreHint);
    document.getElementById("closeDialogButton").addEventListener("click", function() {
        customDialog.style.display = "none";
    });
    


    // obtain generated puzzle from back-end
    function generatePuzzle() {
        const language = document.getElementById('language').value;
        const level = document.getElementById('level').value;

        // AJAX call to the Flask backend to generate a new crossword puzzle
        fetch(`/generate_crossword?language=${language}&level=${level}`)
            .then(response => response.json())
            .then(data => {
                crosswordData = data; // Store the returned data
                displayCrossword(data.puzzle); // Call a function to display the crossword
            })
            .catch(error => console.error('Error:', error));
    }

    // display the puzzle in the grid 
    function displayCrossword(puzzleData) {
        // Clear the previous game and hints
        crosswordContainer.innerHTML = '';
        acrossCluesList.innerHTML = '<h2>Across</h2><ul></ul>';
        downCluesList.innerHTML = '<h2>Down</h2><ul></ul>';

        // Construct and display the puzzle
        const table = document.createElement('table');
        puzzleData[0].forEach((row, rowIndex) => {
            const tr = document.createElement('tr');
            row.forEach((cell, cellIndex) => {
                const td = document.createElement('td');
                td.className = "table-cell";

                if (cell === '') {
                    td.classList.add('empty'); // add the css class for the empty grid
                } else {
                    
                    for (let i=0; i<crosswordData.puzzle[1].length; i++){
                        if (crosswordData.puzzle[1][i][0] == rowIndex && crosswordData.puzzle[1][i][1] == cellIndex){
                            var annotation = document.createElement('div')
                            annotation.className = 'annotation';
                            annotation.textContent = puzzleData[1][i][4];
                            td.appendChild(annotation)   
                        }   
                    } // set horiztonal annotations
                    
                    for (let i=0; i<crosswordData.puzzle[2].length; i++){
                        if (crosswordData.puzzle[2][i][0] == rowIndex && crosswordData.puzzle[2][i][1] == cellIndex){
                            var annotation = document.createElement('div')
                            annotation.className = 'annotation';
                            annotation.textContent = crosswordData.puzzle[2][i][4];
                            td.appendChild(annotation)   
                        }   
                    } // set vertical annotations
                      
                    const input = document.createElement('input');
                    input.id = `r${rowIndex}c${cellIndex}`; // id for the query later
                    input.type = 'text';
                    input.maxLength = '1';
                    td.appendChild(input);
                }
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
        crosswordContainer.appendChild(table);

        // set horizontal hints
        const acrossUl = acrossCluesList.querySelector('ul');
        puzzleData[1].forEach(clue => {
            const li = document.createElement('li');
            li.textContent = `${clue[4]}:\t ${clue[3]}`; // The text location of the hints
            acrossUl.appendChild(li);
        });

        // show the vertical hints
        const downUl = downCluesList.querySelector('ul');
        puzzleData[2].forEach(clue => {
            const li = document.createElement('li');
            li.textContent = `${clue[4]}:\t ${clue[3]}`; // The text location of the hints
            downUl.appendChild(li);
        });

    }


    //global response
    window.generatePuzzle = generatePuzzle; // Assign the function to be called globally


    // reset the game
    function resetGame() {
        // reset the timer
        document.getElementById('timer').textContent = 'Time: 00:00';
        // clear the accuracy
        document.getElementById('accuracy-value').textContent = '--';
        // clear the previous answer
        let inputs = document.querySelectorAll('#crossword-grid input');
        inputs.forEach(input => input.value = '');
        // reset the timer if needed
        stopTimer();
    }

    // display the puzzle answer in the grid
    function showAnswers() {
        // Map of cell positions to input elements
        const cellMap = {};
        const cells = crosswordGrid.querySelectorAll('td');
        cells.forEach((cell, index) => {
            const rowIndex = Math.floor(index / 15); // 15 is the width of the grid
            const colIndex = index % 15;
            cellMap[`${rowIndex},${colIndex}`] = cell;
        });


        
        // Fill in the answers for horizontal words
        crosswordData.puzzle[1].forEach((clue) => {
            const [row, col, word, word_clue, word_number] = clue;
            for (let i = 0; i < word.length; i++) {
                const cellKey = `${row},${col + i}`;
                if (cellMap[cellKey]) {
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = word[i];
                    input.disabled = true;
                    cellMap[cellKey].innerHTML = ''; // Clear the cell
                    cellMap[cellKey].appendChild(input); // Insert the answer
                    
                    for (let j=0; j<crosswordData.puzzle[1].length; j++){
                        if (crosswordData.puzzle[1][j][0] == row && crosswordData.puzzle[1][j][1] == col+i){
                            var annotation = document.createElement('div')
                            annotation.className = 'annotation';
                            annotation.textContent = crosswordData.puzzle[1][j][4];
                            cellMap[cellKey].appendChild(annotation)   
                        }   
                    } // set horiztonal annotations
                    for (let j=0; j<crosswordData.puzzle[2].length; j++){
                        if (crosswordData.puzzle[2][j][0] == row && crosswordData.puzzle[2][j][1] == col + i){
                            var annotation = document.createElement('div')
                            annotation.className = 'annotation';
                            annotation.textContent = crosswordData.puzzle[2][j][4];
                            cellMap[cellKey].appendChild(annotation)   
                        }   
                    } // set horiztonal annotations
                }
            }
        });

        // Fill in the answers for vertical words
        crosswordData.puzzle[2].forEach((clue) => {
            const [row, col, word, word_clue, word_number] = clue;
            for (let i = 0; i < word.length; i++) {
                const cellKey = `${row + i},${col}`;
                if (cellMap[cellKey]) {
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = word[i];
                    input.disabled = true;
                    cellMap[cellKey].innerHTML = ''; // Clear the cell
                    cellMap[cellKey].appendChild(input); // Insert the answer

                    for (let j=0; j<crosswordData.puzzle[1].length; j++){
                        if (crosswordData.puzzle[1][j][0] == row+i && crosswordData.puzzle[1][j][1] == col){
                            var annotation = document.createElement('div')
                            annotation.className = 'annotation';
                            annotation.textContent = crosswordData.puzzle[1][j][4];
                            cellMap[cellKey].appendChild(annotation)   
                        }   
                    } // set horiztonal annotations
                    for (let j=0; j<crosswordData.puzzle[2].length; j++){
                        if (crosswordData.puzzle[2][j][0] == row + i && crosswordData.puzzle[2][j][1] == col){
                            var annotation = document.createElement('div')
                            annotation.className = 'annotation';
                            annotation.textContent = crosswordData.puzzle[2][j][4];
                            cellMap[cellKey].appendChild(annotation)   
                        }   
                    } // set horiztonal annotations
                }
            }
        });
    }

    let num_hit = 0;
    // show the hints
    function showHint() {
        customDialog.style.display = "flex";
        document.getElementById('MoreHintButton').style.display = 'flex';
        customDialogHeader.innerText = 'Words used in the Crossword:'
        let hint_info = ''
        crosswordData.puzzle[4].forEach(hint_word=>{
            if(num_hit<crosswordData.puzzle[4].length/3){
                hint_info = hint_info + hint_word + '\u0020\u0020'
                num_hit += 1;
            };
        })
        customDialogContent.innerText = hint_info;  
        num_hit = 0;
    }

    function showMoreHint() {
        customDialog.style.display = "flex";
        customDialogHeader.innerText = 'Words used in the Crossword:'
        let hint_info = ''
        crosswordData.puzzle[4].forEach(hint_word=>{
            hint_info = hint_info + hint_word + '\u0020\u0020'
        })
        customDialogContent.innerText = hint_info;  
    }

    let timer; // define the timer
    let startTime; // start the time

    

    // check the answer
    function checkAnswers() {
        stopTimer(); // Stop the timer

        let correct = 0;
        let total = crosswordData.puzzle[1].length + crosswordData.puzzle[2].length; // Total number of answers
        let answers = document.querySelectorAll('#crossword-grid input');

        let correct_answers = crosswordData.puzzle[3][0]
        let words_idx = crosswordData.puzzle[3][1]

        // Check the answer 
        words_idx.forEach(word_idx => {
            let correct_word_flag = 1
            word_idx.forEach(idx => {       
                if (correct_answers[idx] != answers[idx].value){
                    correct_word_flag = 0   // this word is wrong if one letter of it is wrong
                }
            });
            if (correct_word_flag == 1){ correct = correct + 1 }  // all letters in a word are correct

        });

        let accuracy = (correct / total) * 100;

        // Calculate the time elapsed
        let currentTime = new Date();
        let timeElapsed = new Date(currentTime - startTime);
        let minutes = timeElapsed.getUTCMinutes().toString().padStart(2, '0');
        let seconds = timeElapsed.getUTCSeconds().toString().padStart(2, '0');

        // Display accuracy and time elapsed in an CustomDialog
        customDialog.style.display = "flex";
        customDialogHeader.innerText = 'Game Score:';
        customDialogContent.innerText = `Words accuracy: ${accuracy.toFixed(2)}%\n Time taken: ${minutes}:${seconds}.`;
        document.getElementById('MoreHintButton').style.display = 'none';

        // Update the accuracy display on the page
        document.getElementById('accuracy-value').textContent = accuracy.toFixed(2);

        // Optionally, you can also update the time display on the page if you have a dedicated element for it
        document.getElementById('time').textContent = `${minutes}:${seconds}`;
    }


    // start the timer
    function startTimer() {
        startTime = new Date();
        timer = setInterval(function() {
            let currentTime = new Date();
            let timeElapsed = new Date(currentTime - startTime);
            let minutes = timeElapsed.getUTCMinutes().toString().padStart(2, '0');
            let seconds = timeElapsed.getUTCSeconds().toString().padStart(2, '0');
            document.getElementById('timer').textContent = `Time: ${minutes}:${seconds}`;
        }, 1000);
    }

    // stop the timer
    function stopTimer() {
        clearInterval(timer);
    }


    // when the document loading completed, star the game
    document.addEventListener('DOMContentLoaded', function() {
        generatePuzzle();
        startTimer();
    });

});




