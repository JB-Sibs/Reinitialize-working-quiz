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
    questions = quiz.question_set.all()

    # Get the current user
    user = request.user

    # Calculate remaining attempts by counting how many times the student has taken the quiz
    attempts_taken = Grade.objects.filter(user=user, quiz=quiz).count()
    attempts_left = quiz.attempts_allowed - attempts_taken

    # If no attempts are left, deny access to the quiz
    if attempts_left <= 0:
        return render(request, 'quiz.html', {
            'quiz': quiz,
            'course': quiz.course,
            'error_message': 'You have no attempts left for this quiz.'
        })

    # Pass the quiz and questions to the template, along with the remaining attempts and time limit
    context = {
        'quiz': quiz,
        'questions': questions,
        'course': quiz.course,
        'attempts_left': attempts_left,  # Remaining attempts
        'time_limit': quiz.time_limit,   # Time limit in minutes
    }

    return render(request, 'quiz.html', context)


def quiz_data_view(request, course_pk, quiz_pk):
    try:
        # Fetch the quiz and its questions
        quiz = Quiz.objects.get(pk=quiz_pk)
        questions = []

        # Loop through the questions and collect answers
        for q in quiz.get_questions():  # Make sure `get_questions()` is defined in your `Quiz` model.
            answers = [a.text for a in q.get_answers()]  # Ensure `get_answers()` is defined in `Question` model.
            questions.append({str(q): answers})

        # Return JSON response
        return JsonResponse({
            'data': questions,
            'time': quiz.time_limit,  # Ensure `time` is an attribute of `Quiz`.
        })

    # Handle the case where the quiz doesn't exist
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Quiz not found'}, status=404)

    # Catch other exceptions and log them for debugging
    except Exception as e:
        print(f"Error: {e}")  # Print the error to server logs for debugging
        return JsonResponse({'error': 'An internal server error occurred'}, status=500)


def create_or_update_quiz_view(request, course_pk=None, quiz_pk=None):
    # Handle both create and update
    if quiz_pk:
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
    else:
        quiz = None

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            saved_quiz = form.save()

            # Debugging: Ensure period is correct
            print(f"Quiz '{saved_quiz.name}' saved with period: {saved_quiz.period}")

            return redirect('some-view')

    else:
        form = QuizForm(instance=quiz)

    return render(request, 'crate_quiz.html', {'form': form})


def save_quiz_view(request, course_pk, quiz_pk):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = request.POST
            user = request.user

            quiz = get_object_or_404(Quiz, pk=quiz_pk)
            print(f"Quiz '{quiz.name}' period is {quiz.period}")

            questions = quiz.question_set.all()

            # Check if the user has exceeded their attempts
            attempts_taken = Grade.objects.filter(user=user, quiz=quiz).count()
            if attempts_taken >= quiz.attempts_allowed:
                return JsonResponse({'error': 'No more attempts allowed'}, status=403)

            # Parse submitted answers
            quiz_answers = {key: value for key, value in data.items() if key != 'csrfmiddlewaretoken'}

            score = 0
            total_questions = questions.count()
            results = []

            for question in questions:
                selected_answer = quiz_answers.get(question.text)
                correct_answer = question.get_correct_answer()

                if selected_answer == correct_answer.text:
                    score += 1
                    results.append({
                        str(question): {
                            'correct': True,
                            'selected_answer': selected_answer,
                            'correct_answer': correct_answer.text
                        }
                    })
                else:
                    results.append({
                        str(question): {
                            'correct': False,
                            'selected_answer': selected_answer or 'None',
                            'correct_answer': correct_answer.text
                        }
                    })

            final_score = (score / total_questions) * 100
            passed = final_score >= quiz.req_score_to_pass

            # Save the grade
            Grade.objects.create(user=user, quiz=quiz, score=score, passed=passed)

            return JsonResponse({
                'success': True,
                'message': 'Quiz submitted successfully!',
                'score': final_score,
                'results': results,
                'passed': passed
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

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
        return redirect('class:course_view', pk=quiz.course.id)  # Redirect to course view

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