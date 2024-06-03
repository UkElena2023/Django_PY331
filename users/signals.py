from anki.settings import TELEGRAM_BOT_TOKEN, YOUR_PERSONAL_CHAT_ID
from django.db.models.signals import post_save
from django.dispatch import receiver
from cards.models import Card
from .telegram_bot import send_telegram_message
import asyncio
import os


@receiver(post_save, sender=Card)
def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        message = f"""
*Создана новая карточка с id:* {instance.pk}
*Автор:* {instance.author}
*Категория:* {instance.category}
*Вопрос:* {instance.question}

        """
        asyncio.run(send_telegram_message(TELEGRAM_BOT_TOKEN, YOUR_PERSONAL_CHAT_ID, message))

