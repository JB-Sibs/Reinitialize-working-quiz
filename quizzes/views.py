from django.shortcuts import render, get_object_or_404
from .models import Quiz
from django.views.generic import ListView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import QuizForm
from .models import Quiz
from questions.models import Question, Answer
from .forms import QuestionForm, AnswerForm
from class_app.models import Course, Grade
from class_app.models import Grade  # Assuming the Grade model is in an app named 'classapp'

class QuizListView(ListView):
    model = Quiz
    template_name = 'course.html'


def quiz_view(request, course_pk, quiz_pk):
    # Fetch the quiz, along with its related course, or return a 404 if not found
    quiz = get_object_or_404(Quiz.objects.select_related('course'), pk=quiz_pk)

    # Get all questions for the quiz
    questions = quiz.question_set.all()

    # Pass the quiz and questions to the template
    context = {
        'quiz': quiz,
        'questions': questions,
        'course': quiz.course,  # Passing the related course as well
    }

    return render(request, 'quiz.html', context)
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
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Log that we received a request
            print("POST request received at save_quiz_view")

            # Extract the POST data
            data = request.POST
            print(f"Received POST data: {data}")

            # Validate CSRF token
            if 'csrfmiddlewaretoken' not in data:
                return JsonResponse({'error': 'CSRF token missing'}, status=400)

            quiz_answers = {}
            for key, value in data.items():
                if key != 'csrfmiddlewaretoken':  # Skip CSRF token
                    quiz_answers[key] = value  # Save the answer for each question

            print(f"Parsed quiz answers: {quiz_answers}")

            # Get the quiz and user data
            quiz = get_object_or_404(Quiz, pk=quiz_pk)
            user = request.user
            questions = quiz.question_set.all()

            # Initialize scoring variables
            score = 0
            total_questions = questions.count()
            results = []

            for question in questions:
                selected_answer = quiz_answers.get(question.text)
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
                    # Answer is correct
                    score += 1
                    results.append({
                        str(question): {
                            'correct': True,
                            'selected_answer': selected_answer,
                            'correct_answer': correct_answer.text
                        }
                    })
                else:
                    # Answer is wrong
                    results.append({
                        str(question): {
                            'correct': False,
                            'selected_answer': selected_answer,
                            'correct_answer': correct_answer.text
                        }
                    })

            # Calculate the final score
            final_score = (score / total_questions) * 100
            print(f"Final score: {final_score}%")

            # Determine if the user passed the quiz
            passed = final_score >= quiz.req_score_to_pass

            # Save the score and result in the Grade model
            grade, created = Grade.objects.get_or_create(
                user=user,
                quiz=quiz,
                defaults={'score': score, 'passed': passed}
            )

            if not created:
                # If a Grade object already exists, update it
                grade.score = score
                grade.passed = passed
                grade.save()

            return JsonResponse({
                'success': True,
                'message': 'Quiz saved successfully!',
                'score': final_score,
                'results': results,
                'passed': passed,
                'passing_score': quiz.req_score_to_pass
            })

        except Exception as e:
            # Log and return any error encountered
            print(f"Error processing quiz submission: {e}")
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

    # If the request isn't a valid POST, return an error
    return JsonResponse({'error': 'Invalid request'}, status=400)

def create_quiz_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)  # Get the course by its primary key

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)  # Do not save to the database yet
            quiz.course = course  # Automatically assign the course to the quiz
            quiz.save()  # Now save the quiz with the course assigned
            return redirect('quizzes:add_question', quiz_id=quiz.pk)  # Redirect to the question adding view
    else:
        # Prefill the course in the form
        form = QuizForm(initial={'course': course})

    return render(request, 'create_quiz.html', {'form': form, 'course': course})

def add_question_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    current_question_count = quiz.question_set.count()  # Track number of questions added

    # Redirect back to course or quiz view once the specified number of questions is reached
    if current_question_count >= quiz.no_of_questions:
        return redirect('quizzes:quiz_prepared', quiz_id=quiz.id, course_pk=quiz.course.id)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            # Add answer choices for the question
            for i in range(4):  # Assuming 4 choices
                Answer.objects.create(
                    text=request.POST.get(f'choice_{i}'),
                    correct=(request.POST.get('correct') == f'choice_{i}'),
                    question=question
                )

            # Redirect to add another question if not yet reached no_of_questions
            return redirect('quizzes:add_question', quiz_id=quiz.id)
    else:
        question_form = QuestionForm(initial={'quiz': quiz})

    return render(request, 'add_question.html', {'form': question_form, 'quiz': quiz})

def quiz_prepared_view(request, course_pk, quiz_id):
    course = Course.objects.get(id=course_pk)  # Assuming you have a Course model
    quizzes = Quiz.objects.filter(course=course)  # Get all quizzes related to this course

    return render(request, 'course.html', {'course': course, 'quizzes': quizzes, 'obj': course})


def quiz_grades(request, slug):
    quiz = get_object_or_404(Quiz, slug=slug)
    grades = Grade.objects.filter(quiz=quiz)

    context = {
        'quiz': quiz,
        'grades': grades,
    }

    return render(request, 'grades.html', context)