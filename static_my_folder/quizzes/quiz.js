document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript file loaded!');
    console.log("Course ID is: ", courseId);

    const currentUrl = window.location.href.split('?')[0];
    const dataUrl = `${currentUrl.endsWith('/') ? currentUrl : currentUrl + '/'}data`;  // Fixed template literal
    const dataUrl_save = `${currentUrl.endsWith('/') ? currentUrl : currentUrl + '/'}save/`;  // Fixed template literal
    const quizBox = document.getElementById('quiz_box');
    const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
    const quizForm = document.getElementById('quiz_form');
    const returnToCourseBtn = document.getElementById('returnToCourseBtn');  // The Return to Course button

     if (returnToCourseBtn) {
        returnToCourseBtn.addEventListener('click', function () {
            const courseUrl = `/course/${courseId}/`;  // Generate the course URL using courseId
            window.location.href = courseUrl;  // Redirect to the course page
        });
    }
    // Fetch quiz data and display it
    $.ajax({
        type: 'GET',
        url: dataUrl,
        success: function (response) {
            if (response.data && Array.isArray(response.data)) {
                const data = response.data;
                quizBox.innerHTML = "";  // Clear existing content

                data.forEach(el => {
                    for (const [question, answers] of Object.entries(el)) {
                        quizBox.innerHTML += `<hr><div class="mb-2"><b>${question}</b></div>`;  // Backticks for template literal
                        answers.forEach(answer => {
                            quizBox.innerHTML += `
                                <div>
                                    <input type="radio" class="ans" id="${question}-${answer}" name="${question}" value="${answer}">
                                    <label for="${question}-${answer}">${answer}</label>
                                </div>`;  // Backticks for template literal
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

    // Handle form submission
    if (quizForm) {
        quizForm.addEventListener('submit', function (e) {
            e.preventDefault();  // Prevent default form submission
            sendData();
        });
    } else {
        console.error('Quiz form not found!');
    }

    // Send form data via AJAX
    function sendData() {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const answers = getSelectedAnswers();  // Collect selected answers

        const data = {
            'csrfmiddlewaretoken': csrfToken,  // Add CSRF token
            ...answers  // Add answers (spread into the data object)
        };

        console.log('Sending data:', data);  // Log the data being sent

        $.ajax({
            type: 'POST',
            url: dataUrl_save,
            data: data,
            success: function (response) {
                console.log('Response:', response);  // Log success response
                handleQuizResult(response);  // Handle the result
            },
            error: function (error) {
                console.error('Error submitting answers:', error);  // Log the error
            }
        });
    }

    // Helper function to collect selected answers
    function getSelectedAnswers() {
        const answers = {};
        const answerElements = document.querySelectorAll('.ans:checked');

        answerElements.forEach(el => {
            const questionId = el.name;  // Use question ID as key
            answers[questionId] = el.value;  // Store the selected answer
        });

        return answers;
    }

    // Handle the quiz result after successful submission
    function handleQuizResult(response) {
        const results = response.results;
        const passingScore = response.passing_score;
        const totalQuestions = results.length;
        let correctAnswers = 0;
        let resultHTML = '';

        results.forEach(res => {
            const question = Object.keys(res)[0];
            const userAnswer = getSelectedAnswers()[question] || 'No answer provided';
            const correctAnswer = res[question]['correct_answer'];

            if (res[question]['correct']) {
                correctAnswers++;
                resultHTML += `
                    <div class="p-3 my-3 bg-success">
                        <b>Question:</b> ${question}<br>
                        <b>Correct Answer:</b> ${correctAnswer}<br>
                        <b>Your Answer:</b> ${userAnswer}
                    </div>`;  // Backticks for template literal
            } else {
                resultHTML += `
                    <div class="p-3 my-3 bg-danger">
                        <b>Question:</b> ${question}<br>
                        <b>Correct Answer:</b> ${correctAnswer}<br>
                        <b>Your Answer:</b> ${userAnswer}
                    </div>`;  // Backticks for template literal
            }
        });

        // Calculate score and display result
        const score = (correctAnswers / totalQuestions) * 100;
        const resultMessage = score >= passingScore
            ? 'Congratulations! You passed the quiz!'
            : 'Unfortunately, you did not pass. Try again!';

        document.getElementById('quizScore').innerText = score.toFixed(2);
        document.getElementById('quizResultMessage').innerText = resultMessage;
        document.getElementById('quizResultsDetails').innerHTML = resultHTML;

        // Show result modal
        resultModal.show();
    }
});
