from typing import Any

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import request
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import CardForm
from .models import Card
from django.views.decorators.cache import cache_page
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


info = {
    "menu": [
        {"title": "Главная",
         "url": "/",
         "url_name": "index"},
        {"title": "О проекте",
         "url": "/about/",
         "url_name": "about"},
        {"title": "Каталог",
         "url": "/cards/catalog/",
         "url_name": "catalog"},
    ],

}


class MenuMixin:
    """
    Класс-миксин для добавления меню в контекст шаблона страницы.
    Добывает и кеширует cards_count, users_count, menu
    """
    timeout = 30

    def get_menu(self):
        """
        Метод добывает меню, кеширует menu
        :return: menu
        """
        menu = cache.get('menu')
        if not menu:
            menu = info['menu']
            cache.set('menu', menu, timeout=self.timeout)

        return menu

    def get_cards_count(self):
        """
        Метод добывает количество карточек, кеширует cards_count
        :return: количество карточек
        """
        cards_count = cache.get('cards_count')
        if not cards_count:
            cards_count = Card.objects.count()
            cache.set('cards_count', cards_count, timeout=self.timeout)

        return cards_count

    def get_users_count(self):
        """
        Метод добывает количество пользователей, кеширует users_count
        :return: количество пользователей
        """
        users_count = cache.get('users_count')
        if not users_count:
            users_count = get_user_model().objects.count()
            cache.set('users_count', users_count, timeout=self.timeout)

        return users_count

    def get_context_data(self, **kwargs):
        """
        Метод для добавления количества карточек, кол-ва пользователей, меню в контекст шаблона страницы
        :return: контекст шаблона страницы
        """

        context = super().get_context_data(**kwargs)
        context['menu'] = self.get_menu()
        context['cards_count'] = self.get_cards_count()
        context['users_count'] = self.get_users_count()
        return context


class IndexView(MenuMixin, TemplateView):
    """
    Класс для представления главной страницы.
    Используется класс-миксин для добавления меню в контекст шаблона главной страницы
    """
    # Указываем путь к шаблону для главной страницы
    template_name = 'main.html'


class AboutView(MenuMixin, TemplateView):
    """
    Класс для представления страницы "О нас".
    Используется класс-миксин для добавления меню в контекст шаблона страницы "О нас"
    """
    # Указываем путь к шаблону для страницы "О нас"
    template_name = 'about.html'


class CardCatalogView(MenuMixin, ListView):
    """
    Класс отображает карточки для представления в каталоге.
    Используется класс-миксин для добавления меню в контекст шаблона страницы Каталога
    """
    # указываем модель для представления
    model = Card
    # Указываем путь к шаблону для детального отображения карточки
    template_name = 'cards/catalog.html'
    context_object_name = 'cards'
    paginate_by = 30

    def get_queryset(self):
        """
        Метод для модификации начального запроса к БД.
        Получает параметры сортировки из GET-запроса
        :return: сет контекста
        """
        # Параметры для сортировки из GET-запроса
        sort = self.request.GET.get('sort', 'upload_date')  # по дате публикации
        order = self.request.GET.get('order', 'desc')  # по убывающему порядку
        search_query = self.request.GET.get('search_query', '')  # поисковый запрос

        # условие для определения направления сортировки
        if order == 'asc':
            order_by = sort
        else:
            order_by = f'-{sort}'

        # Фильтрация карточек по поисковому запросу и сортировка с использованием Q объектов
        # iregex - позволяет сравнивать строки по регулярному выражению в регистронезависимом режиме
        if search_query:
            queryset = Card.objects.filter(
                Q(question__iregex=search_query) |
                Q(answer__iregex=search_query) |
                Q(tags__name__iregex=search_query)
            ).select_related('category').prefetch_related('tags').order_by(order_by).distinct()
        else:
            queryset = Card.objects.select_related('category').prefetch_related('tags').order_by(order_by)
        return queryset

    # Метод для добавления дополнительного контекста
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Метод для добавления дополнительного контекста
        :param kwargs: дополнительные параметры
        :return: словарь с параметрами контекста
        """
        # Получение существующего контекста из базового класса
        context = super().get_context_data(**kwargs)
        # Добавление дополнительных данных в контекст (# меню добавим через MenuMixin)
        context['sort'] = self.request.GET.get('sort', 'upload_date')
        context['order'] = self.request.GET.get('order', 'desc')
        context['search_query'] = self.request.GET.get('search_query', '')
        # меню добавим через MenuMixin
        return context


def get_categories(request):
    """
    Функция возвращает все категории для представления в каталоге
    Не используется в данном проекте
    """
    return render(request, 'base.html', info)


def get_cards_by_category(request, slug):
    """
    Функция возвращает карточки по категории для представления в каталоге
    Не используется в данном проекте
    """
    return HttpResponse(f'Cards by category {slug}')


def get_cards_by_tag(request, tag_id):
    """
    Функция возвращает карточки по тегу для представления в каталоге
    """
    cards = Card.objects.filter(tags__id=tag_id)
    context = {
        'cards': cards,
        'menu': info['menu'],
    }
    return render(request, 'cards/catalog.html', context)


class CardDetailView(MenuMixin, DetailView):
    """
    Класс для детального представления карточки.
    Используется класс-миксин для добавления меню в контекст шаблона страницы для детального отображения карточки
    """
    # указываем модель для представления
    model = Card
    # Указываем путь к шаблону для детального отображения карточки
    template_name = 'cards/card_detail.html'
    # Переопределяем имя переменной в контексте шаблона на 'card' (до этого было 'cards')
    context_object_name = 'card'

    def get_object(self, queryset=None):
        """
        Метод для обновления счетчика просмотров при каждом отображении детальной страницы карточки
        :param queryset: по умолчанию None
        :return:
        """
        # Получаем объект по переданному в URL параметров pk карточки
        object_view = super().get_object(queryset=queryset)
        # Увеличиваем счетчик просмотров на 1
        Card.objects.filter(pk=object_view.pk).update(views=F('views') + 1)
        return object_view


class AddCardCreateView(MenuMixin, LoginRequiredMixin, CreateView):
    """
    Класс для добавления карточек в каталог.
    Используется класс-миксин для добавления меню в контекст шаблона страницы для добавления карточки.
    Используется класс-миксин LoginRequiredMixin для контроля действий незарегистрированного пользователя
    """
    # Указываем модель, с которой работает представление
    model = Card
    # Указываем класс формы для создания карточки
    form_class = CardForm
    # Указываем путь к шаблону страницы с формой добавления карточки
    template_name = 'cards/add_card.html'
    # URL для перенаправления на страницу Каталога после успешного создания карточки
    success_url = reverse_lazy('catalog')
    # имя параметра запроса, в котором хранится URL-адрес, на кот-й пользователь перенаправляется после успешной авт-ции
    redirect_field_name = 'next'

    def form_valid(self, form):
        """
        Метод добавления автора в новые карточки при ее создании
        """
        # Добавляем автора к карточке перед сохранением
        form.instance.author = self.request.user
        # Логика обработки данных формы перед сохранением объекта
        return super().form_valid(form)


class EditCardUpdateView(MenuMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Класс для редактирования карточек в каталоге.
    Используется класс-миксин MenuMixin для добавления меню в контекст шаблона страницы для редактирования карточки.
    Используется класс-миксин LoginRequiredMixin для контроля действий незарегистрированного пользователя.
    Используется класс-миксин UserPassesTestMixin для контроля прав пользователя
    """
    # Указываем модель, с которой работает представление
    model = Card
    # Указываем класс формы для редактирования карточки
    form_class = CardForm
    # Указываем шаблон, который будет использоваться для отображения формы для редактирования карточки
    template_name = 'cards/add_card.html'
    # Имя переменной контекста для карточки
    context_object_name = 'card'
    # URL для перенаправления на страницу Каталога после успешного редактирования карточки
    success_url = reverse_lazy('catalog')
    # Указываем право, которое должен иметь пользователь для доступа к представлению
    permission_required = 'cards.change_card'

    def test_func(self):
        """
        Метод для проверки прав пользователя и доступа к представлению редактирования карточки
        :return:
        """
        card = self.get_object()
        user = self.request.user
        is_moderator = user.groups.filter(name='Модераторы').exists()
        is_administrator = user.is_superuser
        # is_superuser - это булево поле, которое указывает, является ли пользователь суперпользователем
        # is_staff - это булево поле, которое указывает, имеет ли пользователь доступ к административной панели
        return user == card.author or is_moderator or is_administrator


class CardDeleteView(MenuMixin, LoginRequiredMixin, DeleteView):
    """
    Класс для удаления карточек в каталоге.
    Используется класс-миксин для добавления меню в контекст шаблона страницы при удалении карточки.
    Используется класс-миксин LoginRequiredMixin для контроля действий незарегистрированного пользователя
    """
    # Указываем модель, с которой работает представление
    model = Card
    # Указываем шаблон, который будет использоваться для отображения формы подтверждения удаления
    template_name = 'cards/delete_card.html'
    # URL для перенаправления на страницу Каталога после успешного удаления карточки
    success_url = reverse_lazy('catalog')
