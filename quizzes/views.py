from django.shortcuts import render
from .models import Quiz
from django.views.generic import ListView
from django.http import JsonResponse
from questions.models import Question, Answer

class QuizListView(ListView):
    model = Quiz
    template_name = 'course.html'


def quiz_view(request, course_pk, quiz_pk):
    quiz = Quiz.objects.get(pk=quiz_pk)  # Use quiz_pk here
    return render(request, 'quiz.html', {'quiz_info': quiz})

def quiz_data_view(request, course_pk, quiz_pk):
    try:
        # Fetch the quiz and its questions
        quiz = Quiz.objects.get(pk=quiz_pk)
        questions = []
        for q in quiz.get_questions():
            answers = [a.text for a in q.get_answers()]
            questions.append({str(q): answers})

        # Return JSON response
        return JsonResponse({
            'data': questions,
            'time': quiz.time,
        })

    # Handle the case where the quiz doesn't exist
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Quiz not found'}, status=404)

    # Catch other exceptions
    except Exception as e:
        print(f"Error: {e}")  # Print error to server logs for debugging
        return JsonResponse({'error': 'An error occurred'}, status=500)


def save_quiz_view(request, course_pk, quiz_pk):
    # Ensure the request is a POST request and is sent via AJAX
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Extract the POST data
            data = request.POST
            print(f"Received data: {data}")

            # Validate the presence of the CSRF token
            if 'csrfmiddlewaretoken' not in data:
                return JsonResponse({'error': 'CSRF token missing'}, status=400)

            # Initialize dictionary for quiz answers
            quiz_answers = {}

            # Iterate over POST data and skip 'csrfmiddlewaretoken'
            for key, value in data.items():
                if key != 'csrfmiddlewaretoken':  # Skip CSRF token
                    quiz_answers[key] = value  # Save the answer for each question

            print(f"Parsed answers: {quiz_answers}")

            # Fetch the quiz and its related questions
            quiz = Quiz.objects.get(pk=quiz_pk)
            user = request.user
            questions = quiz.question_set.all()  # Get all questions in the quiz

            # Initialize score and results list
            score = 0
            total_questions = questions.count()
            results = []

            # Iterate through all questions in the quiz
            for question in questions:
                # Get the user's answer for the current question
                selected_answer = quiz_answers.get(question.text)

                # Fetch the correct answer from the database
                correct_answer = question.get_correct_answer()

                # If no answer is selected, treat it as wrong
                if not selected_answer:
                    results.append({
                        str(question): {
                            'correct': False,
                            'selected_answer': 'None',
                            'correct_answer': correct_answer.text if correct_answer else 'None'
                        }
                    })
                elif selected_answer == correct_answer.text:
                    # If the selected answer matches the correct answer
                    score += 1
                    results.append({
                        str(question): {
                            'correct': True,
                            'selected_answer': selected_answer,
                            'correct_answer': correct_answer.text
                        }
                    })
                else:
                    # If the selected answer is incorrect
                    results.append({
                        str(question): {
                            'correct': False,
                            'selected_answer': selected_answer,
                            'correct_answer': correct_answer.text
                        }
                    })

            # Calculate the final score as a percentage
            final_score = (score / total_questions) * 100
            print(f"Final score: {final_score}% score: {score}")

            # Check if the user passed or failed based on the required score to pass
            passed = final_score >= quiz.req_score_to_pass

            # Send the score, results, and passing status to the frontend
            return JsonResponse({
                'success': True,
                'message': 'Quiz saved successfully!',
                'score': final_score,
                'results': results,
                'passed': passed,
                'passing_score': quiz.req_score_to_pass  # Send the passing score to the frontend
            })

        except Exception as e:
            # Log and return any error encountered
            print(f"Error processing quiz submission: {e}")
            return JsonResponse({'error': 'An error occurred while processing your submission.'}, status=500)

    # If the request isn't a valid AJAX POST, return an error
    return JsonResponse({'error': 'Invalid request'}, status=400)