document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript file is loaded and executed!');

    const currentUrl = window.location.href.split('?')[0];  // Get current URL without query parameters
    const dataUrl = `${currentUrl.endsWith('/') ? currentUrl : currentUrl + '/'}data`;
    const dataUrl_save = `${currentUrl.endsWith('/') ? currentUrl : currentUrl + '/'}save`;
    const quizBox = document.getElementById('quiz_box');
    const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));  // Initialize Bootstrap modal

    // Fetch quiz data and populate the quiz
    $.ajax({
        type: 'GET',
        url: dataUrl,
        success: function (response) {
            if (response.data && Array.isArray(response.data)) {
                const data = response.data;

                data.forEach(el => {
                    for (const [question, answers] of Object.entries(el)) {
                        // Displaying the question
                        quizBox.innerHTML += `
                            <hr>
                            <div class="mb-2">
                                <b>${question}</b>
                            </div>`;

                        // Displaying the answers (radio buttons)
                        answers.forEach(answer => {
                            quizBox.innerHTML += `
                                <div>
                                    <input type="radio" class="ans" id="${question}-${answer}" name="${question}" value="${answer}">
                                    <label for="${question}-${answer}">${answer}</label>
                                </div>`;
                        });
                    }
                });
            } else {
                console.error('Unexpected response format:', response);
            }
        },
        error: function (error) {
            console.error('Error fetching quiz data:', error);
        }
    });

    // Submit the form and send selected answers
    const quizForm = document.getElementById('quiz_form');
    if (quizForm) {
        const csrf = document.getElementsByName('csrfmiddlewaretoken');

        const sendData = () => {
            const elements = [...document.getElementsByClassName('ans')];  // Get all answer elements
            const data = { 'csrfmiddlewaretoken': csrf[0].value };  // CSRF token for security
            let totalQuestions = 0;
            let correctAnswers = 0;

            // Collect selected answers
            elements.forEach(el => {
                if (el.checked) {
                    data[el.name] = el.value;  // Get the question as the key and selected answer as value
                }
            });

            // Send selected answers to the server
            $.ajax({
                type: 'POST',
                url: dataUrl_save,
                data: data,
                success: function (response) {
                    const results = response.results;
                    const passingScore = response.passing_score;  // Get the required passing score from the server
                    quizForm.classList.add('not-visible');  // Hide the form after submission

                    let resultHTML = '';  // This will store the HTML for the quiz results
                    let totalQuestions = 0;
                    let correctAnswers = 0;

                    // Display quiz results
                    results.forEach(res => {
                        Object.entries(res).forEach(([question, resp]) => {
                            const answer = data[question] || 'No answer provided';
                            const correct = resp['correct_answer'] || 'No correct answer provided';

                            totalQuestions++;

                            // Build the result for each question
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

                    // Calculate the score and check if the student passed
                    const score = (correctAnswers / totalQuestions) * 100;
                    let resultMessage = score >= passingScore
                        ? 'Congratulations! You passed the quiz!'
                        : 'Unfortunately, you did not pass. Try again!';

                    // Update the modal content
                    document.getElementById('quizScore').innerText = score.toFixed(2);  // Show score percentage
                    document.getElementById('quizResultMessage').innerText = resultMessage;
                    document.getElementById('quizResultsDetails').innerHTML = resultHTML;  // Insert detailed results into modal

                    // Show the result modal
                    resultModal.show();
                },
                error: function (error) {
                    console.error('Error submitting answers:', error);
                }
            });
        };

        // Listen for form submission
        quizForm.addEventListener('submit', e => {
            e.preventDefault();
            sendData();
        });
    } else {
        console.error('quizForm element not found!');
    }

    // Handle Return to Course button click
    document.getElementById('returnToCourseBtn').addEventListener('click', function () {
        if (typeof courseId !== 'undefined') {
            window.location.href = `/course/${courseId}/`;  // Dynamically set the course URL
        } else {
            console.error('courseId is not defined!');
        }
    });
});
