document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript file loaded!');
    const currentUrl = window.location.href.split('?')[0];
    const dataUrl = `${currentUrl.endsWith('/') ? currentUrl : currentUrl + '/'}data`;
    const dataUrl_save = `${currentUrl.endsWith('/') ? currentUrl : currentUrl + '/'}save/`;
    const quizBox = document.getElementById('quiz_box');
    const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
    const quizForm = document.getElementById('quiz_form');
    const returnToCourseBtn = document.getElementById('returnToCourseBtn');

    let quizSubmitted = false;  // Prevent multiple submissions

    // Timer functionality
    const timeLimitElement = document.getElementById('time_limit');
    let timeLimit = parseInt(timeLimitElement.innerText) * 60;  // Convert to seconds
    let timerElement = document.getElementById('time_display');

    let timer = setInterval(() => {
        if (timeLimit <= 0) {
            clearInterval(timer);
            alert("Time's up! Submitting your quiz automatically...");
            disableQuizInputs();  // Disable inputs when time's up

            if (!quizSubmitted) {  // Prevent multiple submissions
                quizSubmitted = true;
                sendData();  // Submit quiz data via AJAX
            }
        } else {
            timeLimit -= 1;
            let minutes = Math.floor(timeLimit / 60);
            let seconds = timeLimit % 60;
            timerElement.innerText = `Time Left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        }
    }, 1000);

    // Fetch and display quiz data
    $.ajax({
        type: 'GET',
        url: dataUrl,
        success: function (response) {
            console.log('Quiz data fetched:', response);
            quizBox.innerHTML = '';
            response.data.forEach(el => {
                for (const [question, answers] of Object.entries(el)) {
                    quizBox.innerHTML += `<hr><div class="mb-2"><b>${question}</b></div>`;
                    answers.forEach(answer => {
                        quizBox.innerHTML += `
                            <div>
                                <input type="radio" class="ans" id="${question}-${answer}" name="${question}" value="${answer}">
                                <label for="${question}-${answer}">${answer}</label>
                            </div>`;
                    });
                }
            });
        },
        error: function (error) {
            console.error('Error fetching quiz data:', error);
        }
    });

    // Handle quiz form submission
    if (quizForm) {
        quizForm.addEventListener('submit', function (e) {
            e.preventDefault();
            if (!quizSubmitted) {  // Prevent multiple submissions
                quizSubmitted = true;
                sendData();
            }
        });
    }

    // Send quiz form data via AJAX
    function sendData() {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const answers = getSelectedAnswers();
        const data = {
            'csrfmiddlewaretoken': csrfToken,
            ...answers
        };

        $.ajax({
            type: 'POST',
            url: dataUrl_save,
            data: data,
            success: function (response) {
                console.log('Quiz submission response:', response);
                handleQuizResult(response);
                setTimeout(() => {
                    window.location.href = `/course/${courseId}/`;
                }, 3000);
            },
            error: function (error) {
                console.error('Error submitting quiz data:', error);
            }
        });
    }

    // Helper function to collect selected answers
    function getSelectedAnswers() {
        const answers = {};
        const answerElements = document.querySelectorAll('.ans:checked');
        answerElements.forEach(el => {
            const questionId = el.name;
            answers[questionId] = el.value;
        });
        return answers;
    }

    // Disable inputs when time runs out
    function disableQuizInputs() {
        const inputs = document.querySelectorAll('input.ans');
        inputs.forEach(input => {
            input.disabled = true;
        });
    }

    // Handle quiz result display
    function handleQuizResult(response) {
        // Same code as before for displaying results
    }
});
