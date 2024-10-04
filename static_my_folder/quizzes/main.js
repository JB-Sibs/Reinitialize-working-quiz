console.log('JavaScript file is loaded and executed!');

const modalBtns = [...document.getElementsByClassName('modal-button')];
const modalBody = document.getElementById('modal-body-confirm');
const startBtn = document.getElementById('start-button');
const url = window.location.href;
let selectedPk = null;  // Declare a global variable to store selected pk

if (modalBody && startBtn) {
    modalBtns.forEach(modalBtn =>
        modalBtn.addEventListener('click', () => {
            const pk = modalBtn.getAttribute('data-pk');
            selectedPk = pk;  // Store the pk globally
            const name = modalBtn.getAttribute('data-quiz');
            const numQuestions = modalBtn.getAttribute('data-questions');
            const score_to_pass = modalBtn.getAttribute('data-pass');
            const time = modalBtn.getAttribute('data-time');

            modalBody.innerHTML = `
                <div class="h5 mb-3">Are you sure you want to begin <b>${name}</b>?</div>
                <div class="text-muted">
                    <ul>
                        <li>No of questions: <b>${numQuestions}</b></li>
                        <li>Score to pass: <b>${score_to_pass}%</b></li>
                        <li>Time in mins: <b>${time}</b></li>
                    </ul>
                
            `;
        })
    );

    startBtn.addEventListener('click', () => {
        if (selectedPk) {
            window.location.href = url + selectedPk;
        } else {
            console.log("No quiz selected");
        }
    });
} else {
    console.log("Modal body or start button not found!");
}
