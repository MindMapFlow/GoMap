from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import (
    SubGoal, Direction, DefaultGoal, Goal, DefaultSubGoal,
    GeneralQuestion, GeneralAnswer, UserGoals,
    Specific_Answer, Specific_Question, Point, Step
)
from django.http import JsonResponse
import json

@login_required
def test_view(request):
    directions = Direction.objects.all()
    general_questions = GeneralQuestion.objects.all()
    selected_direction = None
    specific_questions = []

    if request.method == 'POST':
        if 'direction' in request.POST and 'continue' in request.POST:
            # Пользователь выбрал направление
            direction_id = request.POST.get('direction')
            if direction_id:
                try:
                    selected_direction = Direction.objects.get(id=direction_id)
                    specific_questions = Specific_Question.objects.filter(direction=selected_direction)
                except Direction.DoesNotExist:
                    return JsonResponse({'error': 'Направление не найдено'}, status=404)

        elif 'finish' in request.POST:
            # Завершение теста: обработка ответов
            selected_general_answers = [
                int(value) for key, value in request.POST.items() if key.startswith("general_question_")
            ]
            selected_specific_answers = [
                int(value) for key, value in request.POST.items() if key.startswith("specific_question_")
            ]

            points = set()
            for answer_id in selected_general_answers:
                try:
                    answer = GeneralAnswer.objects.get(id=answer_id)
                    points.update(answer.points.all())
                except GeneralAnswer.DoesNotExist:
                    continue

            for answer_id in selected_specific_answers:
                try:
                    answer = Specific_Answer.objects.get(id=answer_id)
                    points.update(answer.points.all())
                except Specific_Answer.DoesNotExist:
                    continue

            user_goals, _ = UserGoals.objects.get_or_create(user=request.user)
            user_goals.goals_point = ",".join(str(p.id) for p in points)
            user_goals.save()

            matching_goals = []
            for goal in DefaultGoal.objects.all():
                goal_points = set(goal.tags.all())
                if goal_points & points:
                    matching_goals.append(goal)

            return render(request, 'result_test.html', {
                'matching_goals': matching_goals,
            })

        elif 'confirm_goals' in request.POST:
            selected_subgoal_ids = request.POST.getlist('selected_subgoals')

            for subgoal_id in selected_subgoal_ids:
                default_subgoal = get_object_or_404(DefaultSubGoal, id=subgoal_id)
                default_goal = default_subgoal.main_goal

                user_goal, _ = Goal.objects.get_or_create(
                    user=request.user,
                    default_goal=default_goal,
                    goal_name=default_goal.goal_view_name
                )

                # Проверка: есть ли уже такая подцель у пользователя
                existing_subgoal = SubGoal.objects.filter(
                    main_goal=user_goal,
                    default_subgoal=default_subgoal,
                    user=request.user
                ).first()

                if existing_subgoal:
                    continue  # Пропускаем, если уже есть такая подцель

                # Создаем новую подцель и шаги
                user_subgoal = SubGoal.objects.create(
                    main_goal=user_goal,
                    default_subgoal=default_subgoal,
                    user=request.user
                )

                user_goal.subgoals.add(user_subgoal)

                for default_step in default_subgoal.default_steps.all():
                    Step.objects.create(
                        subgoal=user_subgoal,
                        step_description=default_step.step_description,
                        default_step=default_step,
                        user=request.user
                    )

            return redirect('gomap_home')


    return render(request, 'test.html', {
        'general_questions': general_questions,
        'directions': directions,
        'specific_questions': specific_questions,
        'selected_direction': selected_direction,
    })

@login_required
def goals(request):
    user_goals = Goal.objects.filter(user=request.user)
    return render(request, 'goals.html', {'user_goals': user_goals})

@login_required
def subgoal_detail(request, pk):
    subgoal = get_object_or_404(SubGoal, pk=pk, user=request.user)
    steps = subgoal.steps.all()
    return render(request, 'subgoal_detail.html', {'subgoal': subgoal, 'steps': steps})

@login_required
def toggle_step_completion(request, step_id):
    step = get_object_or_404(Step, id=step_id, user=request.user)
    step.is_completed = not step.is_completed
    step.save()

    subgoal = step.subgoal
    total_steps = subgoal.steps.count()
    completed_steps = subgoal.steps.filter(is_completed=True).count()
    subgoal.progress_subgoal = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
    subgoal.save()

    goal = subgoal.main_goal
    all_subgoals = goal.get_subgoals()
    if all_subgoals.exists():
        total_progress = sum(sg.progress_subgoal for sg in all_subgoals)
        goal.progress_goal = int(total_progress / all_subgoals.count())
        goal.save()

    return redirect('subgoal_detail', pk=subgoal.pk)
