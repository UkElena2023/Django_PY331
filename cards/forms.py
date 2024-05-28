from django import forms
from .models import Category, Card, Tag
from django.core.exceptions import ValidationError
import re


# проверка при вводе тегов на отсутсвие пробелов
class TagStringValidator:
    def __call__(self, value):
        if ' ' in value:
            raise ValidationError("Теги не должны содержать пробелы!")


class CardForm(forms.ModelForm):
    """
    Форма для создания карточки в каталоге
    """
    def __init__(self, *args, **kwargs):
        super(CardForm, self).__init__(*args, **kwargs)

    # Кастомизированные поля категории и тегов (доработанные под специфику карточки, теги валидируются на пробелы)
    # Для поля категория используется параметр "queryset", чтобы указать допустимые значения.
    # Параметр "empty_label" позволяет указать текст, который будет отображаться в поле выбора.
    # Параметр "label" позволяет указать текст, который будет отображаться в поле названия.
    # widget для категории устанавливаем forms.Select, что позволяет выбрать из списка значений.
    # Параметр "help_text" позволяет указать текст, который будет отображаться в поле подсказки.
    # Параметр "required" Устанавливаем по умолчанию False, чтобы оно было необязательное.
    # widget для тегов устанавливаем forms.TextInput, что позволяет вводить текст в поле ввода.
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Категория не выбрана",
                                      label='Категория', widget=forms.Select(attrs={'class': 'form-control'}))
    tags = forms.CharField(label='Теги', required=False, help_text='Перечислите теги через запятую',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), validators=[TagStringValidator()])

    class Meta:
        model = Card  # Указываем модель, с которой работает форма
        # Указываем, какие поля должны присутствовать в форме и в каком порядке
        fields = ['question', 'answer', 'category', 'tags']
        # Указываем виджеты для полей
        widgets = {
            # widget для вопросов forms.TextInput позволяет вводить текст в поле ввода.
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            # widget для ответов forms.Textarea позволяет установить область для ввода текста.
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 40}),
        }
        # Названия для полей
        labels = {
            'question': 'Вопрос',
            'answer': 'Ответ',
        }

    def clean_tags(self):
        """
        Метод для валидации и преобразование строки тегов в список тегов
        """
        tags_str = self.cleaned_data['tags'].lower()
        tag_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return tag_list

    def save(self, *args, **kwargs):
        """
        Метод для сохранения и очистки текущих тегов, чтобы не было дублирования тегов
        """
        # Мы получаем экземпляр карточки. Без commit=False карточка сохранится в базу данных
        # При попытке сохранения, необработанные теги приведут к ошибке
        # В этом режиме мы получаем только экземпляр карточки.
        instance = super().save(commit=False)
        # Сохраняем карточку в базу данных, чтобы у нее появился id (без id мы не сможем добавить теги)
        instance.save()

        # Функционал для редактирования карточки (старые теги без этого функционала не удаляются, новые теги просто добавляются)
        current_tags = set(self.cleaned_data['tags'])
        existing_tags = set(tag.name for tag in instance.tags.all())

        # Удаляем теги, которые были удалены из формы при редактировании
        for tag in instance.tags.all():
            if tag.name not in current_tags:
                instance.tags.remove(tag)

        # Добавляем новые теги внесенные в форму при редактировании
        for tag_name in current_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)

        return instance
