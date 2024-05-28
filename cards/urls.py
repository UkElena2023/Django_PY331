from django.urls import path
from . import views
# cards/urls.py
# будет иметь префикс в urls/cards/

urlpatterns = [
    path('catalog/', views.CardCatalogView.as_view(), name='catalog'), # Список всех карточек
    path('categories/', views.get_categories, name='categories'),  # Список всех категорий
    path('categories/<slug:slug>/', views.get_cards_by_category, name='category'),  # Карточки по категории
    path('tags/<int:tag_id>/', views.get_cards_by_tag, name='get_cards_by_tag'),  # Карточки по тегу
    path('<int:pk>/detail/', views.CardDetailView.as_view(), name='detail_card_by_id'), # Детальная страница карточки по pk
    path('<int:pk>/edit/', views.EditCardUpdateView.as_view(), name='edit_card'), # Страница с формой редактирования карточки
    path('<int:pk>/delete/', views.CardDeleteView.as_view(), name='delete_card'), # Страница с уведомлением об удалении карточки
    path('add/', views.AddCardCreateView.as_view(), name='add_card') # Страница с формой добавления карточки

]