from django.contrib import admin
from .models import Card
from django.contrib.admin import SimpleListFilter


class CardCodeFilter(SimpleListFilter):
    title = 'Наличие кода'
    parameter_name = 'has_code'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(answer__contains='```')
        elif self.value() == 'no':
            return queryset.exclude(answer__contains='```')


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в админке
    list_display = ('id', 'question', 'category', 'views', 'upload_date', 'status', 'brief_info')
    # Поля, которые будут ссылками
    list_display_links = ('id',)
    # Поля по которым будет поиск
    search_fields = ('question', 'answer')
    # Поля по которым будет фильтрация
    list_filter = ('category', 'upload_date', 'status', CardCodeFilter)
    # Ordering - сортировка
    ordering = ('-upload_date',)
    # List_per_page - количество элементов на странице
    list_per_page = 10
    # Поля, которые можно редактировать
    list_editable = ('views', 'question', 'status')
    actions = ['set_checked', 'set_unchecked']
    fields = ['question', 'answer', 'category', 'status']

    @admin.display(description='Наличие кода', ordering='answer')
    def brief_info(self, card):
        has_code = 'Да' if '```' in card.answer else 'Нет'
        return f'{has_code}'

    # методы для админпанели, чтобы определять статус карточки
    @admin.action(description='Отметить выбранные карточки как проверенные')
    def set_checked(self, request, queryset):
        update_count = queryset.update(status=Card.Status.CHECKED)
        self.message_user(request, f'{update_count} записей было помечено как проверенное')

    @admin.action(description='Отметить выбранные карточки как непроверенные')
    def set_unchecked(self, request, queryset):
        update_count = queryset.update(status=Card.Status.UNCHECKED)
        self.message_user(request, f'{update_count} записей было помечено как непроверенное', 'warning')
    #
