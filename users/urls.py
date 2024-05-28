from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'users'  # Пространство имен для приложения

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),  # маршрут для страницы авторизации
    path('logout/', views.LogoutUser.as_view(), name='logout'),  # маршрут для страницы выхода из аккаунта
    path('signup/', views.RegisterUser.as_view(), name='signup'),  # маршрут для страницы регистрации
    path('thanks/', views.ThanksForRegister.as_view(), name='thanks'),  # маршрут для страницы успешной регистрации

####### группа маршрутов для личного кабинета пользователя - Профиль / Изменение пароля / Мои карточки
    path("profile/", views.ProfileUser.as_view(), name='profile'),  # маршрут для страницы профиля пользователя
    path("password_change/", views.UserPasswordChange.as_view(), name='password_change'),
    # маршрут для страницы смены пароля
    path("password_change_done/", views.UserPasswordChangeDone.as_view(), name='password_change_done'),
    # маршрут с сообщением, что пароль сброшен
    path("profile_cards/", views.UserCardsView.as_view(), name='profile_cards'),
    # маршрут для страницы с карточками пользователя

####### группа маршрутов для Восстановление пароля
    # Маршрут для сброса пароля
    path("password-reset/", views.UserPasswordReset.as_view(), name="password_reset"),

    # Маршрут для подтверждения сброса пароля и уведомления об отправке письма на почту
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"
    ), name="password_reset_done",
         ),

    # Маршрут для ввода нового пароля
    path("reset/<uidb64>/<token>/", views.UserPasswordResetConfirm.as_view(), name="password_reset_confirm"),

    # Маршрут для завершения сброса пароля
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"
    ), name="password_reset_complete",
         ),
]
