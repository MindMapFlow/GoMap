from django.db import models
from django.conf import settings
# Create your models here.

class Direction(models.Model):
    name = models.CharField('Название направления', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"

class Point(models.Model):
    name = models.CharField(max_length=50)#Метка которая в конце повлияет какие цели будут показаны пользователю
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Метка"
        verbose_name_plural = "Метки"
        
class DefaultGoal(models.Model):
  
    goal_view_name = models.CharField('Название системной цели', max_length=50)
    tags = models.ManyToManyField(Point, related_name='default_goals', blank=True)  # Множественный выбор меток


    def __str__(self):
        return self.goal_view_name

    class Meta:
        verbose_name = "Базовая цель"
        verbose_name_plural = "Базовые цели"


class DefaultSubGoal(models.Model):
    main_goal = models.ForeignKey(DefaultGoal, related_name='default_subgoals', on_delete=models.CASCADE)
    sub_goal_name = models.CharField('Название побочной цели', max_length=50)

    def __str__(self):
        return self.sub_goal_name

    class Meta:
        verbose_name = "Базовая побочная цель"
        verbose_name_plural = "Базовые побочные цели"


class DefaultStep(models.Model):
    subgoal = models.ForeignKey(DefaultSubGoal, related_name='default_steps', on_delete=models.CASCADE)
    step_description = models.CharField('Описание шага', max_length=100)

    def __str__(self):
        return self.step_description

    class Meta:
        verbose_name = "Базовый шаг"
        verbose_name_plural = "Базовые шаги"

class Goal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    goal_name = models.CharField('Название цели', max_length=50)
    progress_goal = models.IntegerField(default=0)

    default_goal = models.ForeignKey(
        'DefaultGoal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Базовая цель"
    )

    subgoals = models.ManyToManyField('SubGoal', related_name='goals', blank=True)
 
    def __str__(self):
        return self.goal_name

    def get_subgoals(self):
        return self.subgoals.all()

    @property
    def progress(self):
        subgoals = self.all_subgoals()
        if not subgoals.exists():
            return 0
        total = 0
        for subgoal in subgoals:
            total += subgoal.progress_subgoal
        return round(total / subgoals.count(), 2)
    class Meta:
        verbose_name = "Цель пользователя"
        verbose_name_plural = "Цели пользователей"


class SubGoal(models.Model):
    main_goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='all_subgoals')
    progress_subgoal = models.IntegerField(default=0)

    # Привязка к дефолтной подцели
    default_subgoal = models.ForeignKey(
        'DefaultSubGoal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Базовая побочная цель"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="subgoals",default=1
    )

    def __str__(self):
        if self.default_subgoal:
             return self.default_subgoal.sub_goal_name
        return f"SubGoal (id={self.id})"
    
    
    @property
    def progress(self):
        steps = self.steps.all()
        if not steps.exists():
            return 0
        done = steps.filter(is_done=True).count()
        return round((done / steps.count()) * 100, 2)
    class Meta:
        verbose_name = "Побочная цель пользователя"
        verbose_name_plural = "Побочные цели пользователей"


class Step(models.Model):
    subgoal = models.ForeignKey(SubGoal, related_name='steps', on_delete=models.CASCADE)
    step_description = models.CharField('Описание шага', max_length=100)
    is_completed = models.BooleanField(default=False, verbose_name="Выполнено")

    # Привязка к дефолтному шагу
    default_step = models.ForeignKey(
        'DefaultStep',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Базовый шаг"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="steps",
        default=1
    )

    def __str__(self):
        return self.step_description

    class Meta:
        verbose_name = "Шаг пользователя"
        verbose_name_plural = "Шаги пользователей"
class GeneralQuestion(models.Model):
    text = models.CharField(max_length=255)  # Текст вопроса

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Общий вопрос"
        verbose_name_plural = "Общие вопросы"
        
class GeneralAnswer(models.Model):
    question = models.ForeignKey(GeneralQuestion, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)  # Текст ответа
    points = models.ManyToManyField('Point', related_name='general_answers')
   

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = "Общий ответ"
        verbose_name_plural = "Общие ответы"
        
class Specific_Question(models.Model):
    direction = models.ForeignKey(Direction, related_name='specific_questions', on_delete=models.CASCADE, verbose_name='Направление', default=1) 
    text = models.CharField(max_length=255, verbose_name='Текст вопроса')
    
    def __str__(self):
        return f"{self.direction.name} — {self.text}"

    class Meta:
        verbose_name = "Специфичный вопрос"
        verbose_name_plural = "Специфичные вопросы"


class Specific_Answer(models.Model):
    question = models.ForeignKey(Specific_Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255, verbose_name='Текст ответа')
    points = models.ManyToManyField(Point, related_name='specific_answers', verbose_name='Метки')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Специфичный ответ"
        verbose_name_plural = "Специфичные ответы"
class UserGoals(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goals_point = models.CharField(max_length=255, blank=True)  # Строка меток, присвоенных пользователю

    def assign_goals(self):
        # Разбиваем строку меток на список
        user_points = set(self.goals_point.split(","))
        
        # Ищем цели, которые содержат хотя бы одну общую метку с пользовательскими метками
        matching_goals = DefaultGoal.objects.filter(tags__in=user_points).distinct()
        
        for goal in matching_goals:
            Goal.objects.get_or_create(user=self.user, goal_name=goal.goal_view_name, default_goal=goal)
