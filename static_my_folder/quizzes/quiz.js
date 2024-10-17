document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript file loaded!');
    const currentUrl = window.location.href.split('?')[0];
    const dataUrl = `${currentUrl.endsWith('/') ? currentUrl : currentUrl + '/'}data/`;
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

    // Check if there is stored time in localStorage
    let storedTime = localStorage.getItem('remainingTime');
    if (storedTime !== null) {
        timeLimit = parseInt(storedTime);  // Retrieve stored time if available
    }

    let timer = setInterval(() => {
        if (timeLimit <= 0) {
            clearInterval(timer);
            localStorage.removeItem('remainingTime'); // Clear storage when time is up
            if (!quizSubmitted) {
                quizSubmitted = true;
                alert("Time's up! Submitting your quiz automatically...");
                sendData();
            }
        } else {
            timeLimit -= 1;
            let minutes = Math.floor(timeLimit / 60);
            let seconds = timeLimit % 60;
            timerElement.innerText = `Time Left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            localStorage.setItem('remainingTime', timeLimit);  // Store the remaining time
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
            if (!quizSubmitted) {
                quizSubmitted = true;
                localStorage.removeItem('remainingTime');  // Clear the stored time upon submission
                sendData();
            }
        });
    }

    // Send quiz form data via AJAX
    function sendData() {
        disableQuizInputs(); // Disable inputs to prevent further changes
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
                const results = response.results;
                quizForm.classList.add('not-visible');

                let resultHTML = '';
                let totalQuestions = 0;
                let correctAnswers = 0;

                // Process the quiz results
                results.forEach(res => {
                    Object.entries(res).forEach(([question, resp]) => {
                        const answer = data[question] || 'No answer provided';
                        const correct = resp['correct_answer'] || 'No correct answer provided';

                        totalQuestions++;

                        if (resp.correct) {
                            correctAnswers++;
                            resultHTML += `
                                <div class="p-3 my-3 bg-success">
                                    <b>Question:</b> ${question}<br>
                                    Correct Answer: ${correct}<br>
                                    Your Answer: ${answer}
                                </div>`;
                        } else {
                            resultHTML += `
                                <div class="p-3 my-3 bg-danger">
                                    <b>Question:</b> ${question}<br>
                                    Correct Answer: ${correct}<br>
                                    Your Answer: ${answer}
                                </div>`;
                        }
                    });
                });

                // Calculate the final score
                const score = Math.round((correctAnswers / totalQuestions) * 100); // Round to nearest whole number
                document.getElementById('quizScore').innerText = score.toFixed(2);  // Show the score

                // Show results
                document.getElementById('quizResultsDetails').innerHTML = resultHTML;
                resultModal.show();
            },
            error: function (error) {
                console.error('Error submitting quiz data:', error);
            }
        });
    }

    function getSelectedAnswers() {
        const answers = {};
        const answerElements = document.querySelectorAll('.ans:checked');
        answerElements.forEach(el => {
            const questionId = el.name;
            answers[questionId] = el.value;
        });
        return answers;
    }

    function disableQuizInputs() {
        const inputs = document.querySelectorAll('input.ans');
        inputs.forEach(input => {
            input.disabled = true;
        });
    }

    returnToCourseBtn.addEventListener('click', function() {
        window.location.href = `/course/${courseId}/`;
    });
});
