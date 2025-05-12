from django.contrib import admin
from django import forms
from .models import Specific_Question, Specific_Answer, Direction, DefaultGoal, DefaultSubGoal, DefaultStep, Point, GeneralAnswer, GeneralQuestion, Goal, SubGoal, Step

# Регистрируем модели
admin.site.register(Direction)

admin.site.register(DefaultSubGoal)
admin.site.register(DefaultStep)
admin.site.register(GeneralQuestion)
admin.site.register(GeneralAnswer)
admin.site.register(Specific_Question)
admin.site.register(Specific_Answer)
admin.site.register(Goal)
admin.site.register(SubGoal)
admin.site.register(Step)


from .models import DefaultGoal, Point

class DefaultGoalAdmin(admin.ModelAdmin): # Отображаем имя цели и направление
    filter_horizontal = ('tags',)  # Удобное отображение выбора меток для целей

admin.site.register(DefaultGoal, DefaultGoalAdmin)
admin.site.register(Point)
# Регистрируем модели в админке
