from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetConfirmView
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model

from cards.views import MenuMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from users.forms import LoginUserForm, RegisterUserForm, UserPasswordResetForm, UserPasswordResetConfirmForm
from .forms import ProfileUserForm, UserPasswordChangeForm
from cards.models import Card


class LoginUser(MenuMixin, LoginView):
    """
    Класс для авторизации пользователя.
    Используется класс-миксин для добавления меню в контекст шаблона страницы для авторизации пользователя.
    """
    # указываем класс формы для авторизации пользователя
    form_class = LoginUserForm
    # Указываем путь к шаблону для страницы для авторизации пользователя
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}  # экстра контекст для шаблона страницы авторизации пользователя
    # Перенаправление на страницу после успешной авторизации с которой пользователь пришел
    redirect_field_name = 'next'

    def get_success_url(self):
        """
        Метод для перенаправления на страницу, с которой пользователь был направлен на авторизацию
        """
        if self.request.POST.get('next', '').strip():
            # Перенаправление на страницу, с которой пользователь был направлен на авторизацию
            return self.request.POST.get('next')
        # Перенаправление на страницу каталога после неудачной авторизации
        return reverse_lazy('catalog')


class LogoutUser(MenuMixin, LogoutView):
    """
    Класс для выхода пользователя из системы.
    Используется класс-миксин для добавления меню в контекст шаблона страницы для выхода пользователя.
    """
    # Указываем путь к шаблону об успешном выхода пользователя из системы
    template_name = 'users/logout.html'


class RegisterUser(MenuMixin, CreateView):
    """
    Класс для регистрации пользователя на базе CreateView.
    Используется класс-миксин для добавления меню в контекст шаблона страницы для выхода пользователя.
    """
    # Указываем класс формы, который мы создали для регистрации
    form_class = RegisterUserForm
    # Путь к шаблону, который будет использоваться для отображения формы
    template_name = 'users/register.html'
    # Дополнительный контекст для передачи в шаблон
    extra_context = {'title': 'Регистрация'}
    # URL, на который будет перенаправлен пользователь после успешной регистрации
    success_url = reverse_lazy('users:thanks')


class ThanksForRegister(MenuMixin, TemplateView):
    """
    Класс для представления страницы успешной регистрации пользователя.
    Используется класс-миксин для добавления меню в контекст шаблона страницы успешной регистрации пользователя.
    """
    # Указываем путь к шаблону для страницы успешной регистрации пользователя
    template_name = 'users/thanks.html'
    extra_context = {'title': 'Регистрация завершена'}


class ProfileUser(MenuMixin, LoginRequiredMixin, UpdateView):
    """
    Класс для редактирования профиля пользователя.
    Используется класс-миксин для добавления меню в контекст шаблона страницы для редактирования профиля пользователя.
    Используется класс-миксин LoginRequiredMixin для контроля действий незарегистрированного пользователя.
    """
    model = get_user_model()  # Используем модель текущего пользователя
    form_class = ProfileUserForm  # Связываем с формой профиля пользователя
    template_name = 'users/profile.html'  # Указываем путь к шаблону
    extra_context = {'title': 'Профиль пользователя',
                     'active_tab': 'profile'}  # Дополнительный контекст для передачи в шаблон

    def get_success_url(self):
        # URL, на который переадресуется пользователь после успешного обновления
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        # Возвращает объект модели, который должен быть отредактирован
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            user.moderator = True
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    """
    Класс для изменения пароля пользователя. Наследуется от PasswordChangeView - стандартного класса для изменения
    пароля. Использует пользовательскую форму UserPasswordChangeForm, которая наследуется от PasswordChangeForm
    """
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change_form.html'
    extra_context = {'title': 'Изменение пароля',
                     'active_tab': 'password_change'}
    success_url = reverse_lazy('users:password_change_done')


class UserPasswordChangeDone(TemplateView):
    """
    Класс для представления страницы с сообщением успешного изменения пароля пользователя.
    Наследуется от TemplateView
    """
    template_name = 'users/password_change_done.html'
    extra_context = {'title': 'Пароль изменен успешно'}


class UserCardsView(ListView):
    """
    Класс для отображения всех карточек пользователя. Наследуется от ListView.
    Переопределяет метод get_queryset для получения карточек пользователя
    """
    model = Card
    template_name = 'users/profile_cards.html'
    context_object_name = 'cards'
    extra_context = {'title': 'Мои карточки',
                     'active_tab': 'profile_cards'}

    def get_queryset(self):
        """
        Метод для получения карточек пользователя с помощью фильтра по автору и сортировки по дате загрузки
        """
        return Card.objects.filter(author=self.request.user).order_by('-upload_date')


class UserPasswordReset(PasswordResetView):
    """
    Класс для восстановления пароля пользователя.
    Наследуется от PasswordResetView - стандартного класса для восстановления.
    Запрашивает email для отправки письма со ссылкой для сброса пароля
    """
    form_class = UserPasswordResetForm
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class UserPasswordResetConfirm(PasswordResetConfirmView):
    """
    Класс для ввода нового пароля пользователя.
    Наследуется от PasswordResetConfirmView - стандартного класса для восстановления.
    """
    form_class = UserPasswordResetConfirmForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')




