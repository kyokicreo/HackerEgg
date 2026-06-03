import os
import sys
import django
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async


BOT_TOKEN = "8143436636:AAHf6gryhDH5PuEl3zTygIj2zs2v8sf34uE"
DJANGO_PROJECT_PATH = r'C:\Users\kyoki\Desktop\To_download\BackEndPart'
DJANGO_SETTINGS_MODULE = 'config.settings'


sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

django.setup()

from accounts.models import TelegramLinkCode


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@sync_to_async
def connect_telegram_account(code, telegram_id, telegram_username):
    try:
        link_code = TelegramLinkCode.objects.select_related("user").get(code=code)
    except TelegramLinkCode.DoesNotExist:
        return False, "Код привязки не найден или уже недействителен."

    if link_code.is_used:
        return False, "Этот код уже был использован."

    user = link_code.user

    user.telegram_id = telegram_id
    user.telegram_username = telegram_username
    user.telegram_connected = True
    user.save()

    link_code.is_used = True
    link_code.save()

    return True, "Telegram успешно подключён к аккаунту."


@dp.message(Command("start"))
async def start_handler(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "Привет. Чтобы подключить аккаунт, нажми кнопку подключения Telegram в профиле сайта."
        )
        return

    code = args[1].strip()

    success, text = await connect_telegram_account(
        code=code,
        telegram_id=message.from_user.id,
        telegram_username=message.from_user.username,
    )

    await message.answer(text)


async def main():
    print("Starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())