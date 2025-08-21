import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto

from bot import bot
from config import ADMIN_IDS, AUTO_PUSH_RUNNING, LOCALIZATION_LANG, TIMEZONE, AUTO_PUSH_DAY, SPONSOR_CHANNEL_LINK
from db.utils import get_all_users_unblock, pin_message
from keyboard import kb_button
from lexicon_autopost import dct_autopost

router = Router()
logger = logging.getLogger(__name__)

# Глобальные переменные для управления рассылкой
auto_push_task = None


@router.message(Command("start_push1", "start_push2", "start_push3", "start_push4",
                        "start_push5", "start_push6", "start_push7", "start_push8",
                        "start_push9", "start_push10", "start_push11", "start_push12"))
async def start_push_command(message: types.Message):
    global auto_push_task

    if message.from_user.id not in ADMIN_IDS:
        return

    if AUTO_PUSH_RUNNING[0]:
        await message.answer("Авторассылка уже запущена!")
        return

    # Извлекаем номер дня из команды
    day = int(message.text.split('start_push')[1])

    if day not in range(1, 13):
        await message.answer("День должен быть от 1 до 12")
        return

    AUTO_PUSH_DAY[0] = day
    AUTO_PUSH_RUNNING[0] = True

    auto_push_task = asyncio.create_task(auto_push_process())
    await message.answer(f"Авторассылка запущена с дня {day}!")


@router.message(Command("stop_push"))
async def stop_push_command(message: types.Message):
    global auto_push_task

    if message.from_user.id not in ADMIN_IDS:
        return

    if not AUTO_PUSH_RUNNING[0]:
        await message.answer("Авторассылка не запущена!")
        return

    AUTO_PUSH_RUNNING[0] = False
    if auto_push_task:
        auto_push_task.cancel()
    await message.answer("Авторассылка остановлена!")


async def auto_push_process():
    global AUTO_PUSH_DAY

    while AUTO_PUSH_RUNNING[0]:
        current_day = AUTO_PUSH_DAY[0]
        day_messages = dct_autopost.get(current_day, [])

        # Сортируем сообщения по времени
        sorted_day_messages = sorted(day_messages, key=lambda x: datetime.strptime(x['time'], '%H:%M').time())
        # Проверяем все сообщения для текущего дня
        for msg in sorted_day_messages:

            if not AUTO_PUSH_RUNNING[0]:
                break

            # Получаем текущее время
            now = datetime.now(TIMEZONE)
            current_time = now.strftime('%H:%M')

            # Если время сообщения еще не наступило, ждем
            if msg['time'] >= current_time:
                # Вычисляем время до отправки
                msg_datetime = datetime.combine(now.date(),
                                                datetime.strptime(msg['time'], '%H:%M').time())
                msg_datetime = TIMEZONE.localize(msg_datetime)

                wait_seconds = (msg_datetime - now).total_seconds()
                if wait_seconds > 0:
                    logger.info(f"Ждем {wait_seconds} секунд до сообщения в {msg['time']}")
                    await asyncio.sleep(wait_seconds)

                # Отправляем сообщение
                if AUTO_PUSH_RUNNING[0]:
                    await send_auto_message(msg)

        # Переходим к следующему дню
        AUTO_PUSH_DAY[0] += 1
        if AUTO_PUSH_DAY[0] > 12:
            AUTO_PUSH_DAY[0] = 1  # Начинаем с 5 дня снова

        # Ждем до следующего дня
        now = datetime.now(TIMEZONE)
        tomorrow = now + timedelta(days=1)
        tomorrow_start = datetime.combine(tomorrow.date(), datetime.min.time())
        tomorrow_start = TIMEZONE.localize(tomorrow_start)

        wait_seconds = (tomorrow_start - now).total_seconds()
        if wait_seconds > 0 and AUTO_PUSH_RUNNING[0]:
            logger.info(f"Ждем {wait_seconds} секунд до следующего дня")
            await asyncio.sleep(wait_seconds)


async def send_auto_message(message_info: dict):
    keyboard = kb_button('✅ Mein Kanal', SPONSOR_CHANNEL_LINK.split('?')[0])
    msg_type = message_info['type']
    media_id = message_info['media_id']
    status = message_info['status']
    text = message_info['text'][LOCALIZATION_LANG]  # Используем русскую версию

    # Получаем пользователей
    users_in = await get_all_users_unblock('users_1')
    users_out = await get_all_users_unblock('users_2')

    count_in = 0
    count_out = 0

    try:
        if msg_type == 'text':
            # Рассылка текстового сообщения
            if status == 'in_chanel':
                for user_id in users_in:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        sent_message = await bot.send_message(user_id, text, parse_mode='HTML', reply_markup=keyboard)
                        await pin_message(user_id, sent_message.message_id)
                        count_in += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки in_chanel {user_id}: {e}")
            if status == 'not_in_chanel':
                for user_id in users_out:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        sent_message = await bot.send_message(user_id, text, parse_mode='HTML', reply_markup=keyboard)
                        await pin_message(user_id, sent_message.message_id)
                        count_out += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки out_chanel {user_id}: {e}")

        elif msg_type == 'photo':
            # Рассылка фото с текстом
            if status == 'in_chanel':
                for user_id in users_in:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        sent_message = await bot.send_photo(user_id, media_id, caption=text, parse_mode='HTML', reply_markup=keyboard)
                        await pin_message(user_id, sent_message.message_id)
                        count_in += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки фото in_chanel {user_id}: {e}")
            if status == 'not_in_chanel':
                for user_id in users_out:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        sent_message = await bot.send_photo(user_id, media_id, caption=text, parse_mode='HTML', reply_markup=keyboard)
                        await pin_message(user_id, sent_message.message_id)
                        count_out += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки фото out_chanel {user_id}: {e}")

        elif msg_type == 'video_note':
            # Рассылка видео-сообщения (сначала текст, потом видео)
            if status == 'in_chanel':
                for user_id in users_in:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        sent_message = await bot.send_message(user_id, text, parse_mode='HTML', reply_markup=keyboard)
                        await pin_message(user_id, sent_message.message_id)
                        await asyncio.sleep(0.1)
                        sent_message = await bot.send_video_note(user_id, media_id)
                        await pin_message(user_id, sent_message.message_id)
                        count_in += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки видео in_chanel {user_id}: {e}")
            if status == 'not_in_chanel':
                for user_id in users_out:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        sent_message = await bot.send_message(user_id, text, parse_mode='HTML', reply_markup=keyboard)
                        await pin_message(user_id, sent_message.message_id)
                        await asyncio.sleep(0.1)
                        sent_message = await bot.send_video_note(user_id, media_id)
                        await pin_message(user_id, sent_message.message_id)
                        count_out += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки видео out_chanel {user_id}: {e}")
        elif msg_type == 'media_group':
            # Рассылка медиагруппы
            if status == 'in_chanel':
                for user_id in users_in:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        media_group = [
                            InputMediaPhoto(
                                media=media_id[0],
                                caption=text,
                                parse_mode='HTML',
                                reply_markup=keyboard
                            )
                        ]
                        # Добавляем остальные фото без подписи
                        for media in media_id[1:]:
                            media_group.append(InputMediaPhoto(media=media))

                        # Отправляем медиагруппу
                        sent_message = await bot.send_media_group(chat_id=user_id, media=media_group)

                        count_in += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки видео in_chanel {user_id}: {e}")
            if status == 'not_in_chanel':
                for user_id in users_out:
                    if not AUTO_PUSH_RUNNING[0]:
                        break
                    try:
                        media_group = [
                            InputMediaPhoto(
                                media=media_id[0],
                                caption=text,
                                parse_mode='HTML'
                            )
                        ]
                        # Добавляем остальные фото без подписи
                        for media in media_id[1:]:
                            media_group.append(InputMediaPhoto(media=media))

                        # Отправляем медиагруппу
                        sent_message = await bot.send_media_group(chat_id=user_id, media=media_group)

                        count_out += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Ошибка отправки видео out_chanel {user_id}: {e}")

    except Exception as e:
        logger.error(f"Общая ошибка при рассылке: {e}")

    # Отправляем статистику админам
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"✅ Сообщение отправлено:\n"
                f"• Подписанным: {count_in}\n"
                f"• Неподписанным: {count_out}"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки статистики админу {admin_id}: {e}")