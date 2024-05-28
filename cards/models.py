from django.contrib.auth import get_user_model
from django.db import models


class Card(models.Model):
    class Status(models.IntegerChoices):
        UNCHECKED = 0, "Не проверено"
        CHECKED = 1, "Проверено"

    id = models.AutoField(primary_key=True, db_column='CardID', verbose_name='ID карточки')
    question = models.CharField(max_length=255, db_column='Question', verbose_name='Вопрос')
    answer = models.TextField(max_length=5000, db_column='Answer', verbose_name='Ответ')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_column='CategoryID', verbose_name='Категория')
    upload_date = models.DateTimeField(auto_now_add=True, db_column='UploadDate', verbose_name='Дата публикации')
    views = models.IntegerField(default=0, db_column='Views', verbose_name='Просмотры')
    adds = models.IntegerField(default=0, db_column='Favorites', verbose_name='В избранном')
    tags = models.ManyToManyField('Tag', through='CardTag', related_name='cards', verbose_name='Теги')
    status = models.BooleanField(default=False, choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                 verbose_name='Проверено')
    # функция get_user_model() добывает актуальную модель пользователя из django.contrib.auth.models
    # в таблице Cards добавляется поле author_id
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='cards', null=True,
                               default=None, verbose_name='Автор')

    class Meta:
        db_table = 'Cards'  # имя таблицы в базе данных
        verbose_name = 'Карточка'  # имя в единственном числе для администратора
        verbose_name_plural = 'Карточки'  # имя во множественном числе для администратора

    def __str__(self):
        return f'Карточка {self.question} - {self.answer[:50]}'

    def get_absolute_url(self):
        return f'/cards/{self.id}/detail/'


class Tag(models.Model):
    id = models.AutoField(primary_key=True, db_column='TagID')
    name = models.CharField(max_length=100, db_column='Name')

    class Meta:
        db_table = 'Tags'  # имя таблицы в базе данных
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Тег {self.name}'


class CardTag(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, db_column='CardID')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_column='TagID')

    class Meta:
        db_table = 'CardTags'  # имя таблицы в базе данных
        verbose_name = 'Тег Карточки'
        verbose_name_plural = 'Тег Карточек'

        # уникальность пары тега и карточки
        unique_together = ('card', 'tag')

    def __str__(self):
        return f'Тег {self.tag.name} и карточка {self.card.question}'


class Category(models.Model):
    id = models.AutoField(primary_key=True, db_column='CategoryID')
    name = models.CharField(max_length=100, db_column='Name')

    class Meta:
        db_table = 'Categories'  # имя таблицы в базе данных
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name}'
