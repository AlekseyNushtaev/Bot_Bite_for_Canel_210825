import datetime
from typing import Optional, List

from sqlalchemy import select, func

from bot import bot
from config import TIMEZONE
from db.models import Session, User, PinnedMessage


async def user_exists(user_id: int) -> bool:
    async with Session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None


async def add_user(
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
        sub_id: Optional[str]
) -> None:
    async with Session() as session:
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            sub_id=sub_id,
            time_start=datetime.datetime.now(TIMEZONE)
        )
        session.add(user)
        await session.commit()


async def update_messages_to_del(user_id: int, messages: str) -> None:
    """
    Обновляет поле messages_to_del для указанного пользователя

    :param user_id: Telegram ID пользователя
    :param messages: Строка с сообщениями для удаления
    """
    async with Session() as session:
        # Получаем пользователя из базы
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Обновляем поле и сохраняем изменения
            user.messages_to_del = messages
            await session.commit()
        else:
            # Обработка случая, когда пользователь не найден
            raise ValueError(f"User with ID {user_id} not found in database")


async def delete_messages(user_id: int):

    async with Session() as session:
        stmt = select(User.messages_to_del).where(User.user_id == user_id)
        result = await session.execute(stmt)
        messages_data = result.scalar_one_or_none()
    if messages_data:
        message_ids = [int(msg_id) for msg_id in messages_data.split(',')]
        for msg_id in message_ids:
            try:
                await bot.delete_message(chat_id=user_id, message_id=msg_id)
            except:
                pass


async def get_user_by_id(user_id: int) -> dict:
    """
    Возвращает все данные пользователя в виде словаря по-заданному user_id.

    :param user_id: Telegram ID пользователя
    :return: Словарь с данными пользователя или None, если пользователь не найден
    """
    async with Session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Преобразуем объект User в словарь
            return {column.name: getattr(user, column.name) for column in User.__table__.columns}
        return None


async def update_user(user_dict: dict) -> None:
    """
    Обновляет данные пользователя на основе переданного словаря.

    :param user_dict: Словарь с данными для обновления. Должен содержать 'user_id'
    """
    user_id = user_dict.get("user_id")
    if not user_id:
        raise ValueError("User ID is required for update")

    async with Session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # Обновляем только разрешенные поля
        allowed_fields = ["like_counter", "video_counter", "time_stop", "messages_to_del", "balance", "is_gift",
                          "in_chanel", "status", "user_is_block", "is_gift_2", "time_chanel_in", "time_chanel_out",
                          "time_block", "time_unblock"]
        for field, value in user_dict.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        await session.commit()
        print('obnovlen')


async def update_user_blocked(user_id):
    async with Session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.user_is_block = True
            user.time_block = datetime.datetime.now(TIMEZONE)
            await session.commit()


async def update_user_unblocked(user_id):
    async with Session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.user_is_block = False
            user.time_unblock = datetime.datetime.now(TIMEZONE)
            await session.commit()


async def add_user_without_start(user_id, username, first_name, last_name):
    user_in_db = await user_exists(user_id)
    if not user_in_db:
        await add_user(user_id,
                       username,
                       first_name,
                       last_name,
                       '000')


async def get_stats(period: str) -> dict:
    async with Session() as session:
        # Определение временного интервала
        now = datetime.datetime.now(TIMEZONE)
        if period == '24h':
            start_time = now - datetime.timedelta(hours=24)
        elif period == '7d':
            start_time = now - datetime.timedelta(days=7)
        else:
            start_time = datetime.datetime.min  # Все время

        # Запросы для разных метрик
        started = await session.scalar(
            select(func.count(User.user_id)).where(
                User.time_start >= start_time
            )
        )

        blocked = await session.scalar(
            select(func.count(User.user_id)).where(
                User.user_is_block == True,
                User.time_block >= start_time
            )
        )

        subscribed = await session.scalar(
            select(func.count(User.user_id)).where(
                User.time_chanel_in >= start_time
            )
        )

        unsubscribed = await session.scalar(
            select(func.count(User.user_id)).where(
                User.time_chanel_out >= start_time
            )
        )

    return {
        'started': started,
        'blocked': blocked,
        'subscribed': subscribed,
        'unsubscribed': unsubscribed
    }


async def get_all_users_unblock(status: str) -> dict:
    """
    Возвращает словарь {user_id: sub_id} в зависимости от статуса подписки.
    :param status: 'users_1' - подписанные, 'users_2' - не подписанные, 'users_3' - все
    :return: dict - словарь {user_id: sub_id}
    """
    async with Session() as session:
        # Выбираем нужные поля: user_id и sub_id
        query = select(User.user_id, User.sub_id).where(User.user_is_block == False)

        if status == 'users_1':
            query = query.where(User.in_chanel == True)
        elif status == 'users_2':
            query = query.where(User.in_chanel == False)

        result = await session.execute(query)
        # Формируем словарь {user_id: sub_id}
        return {row.user_id: row.sub_id for row in result.all()}


def format_time_remaining(target_datetime):
    now = datetime.datetime.now(TIMEZONE)
    if target_datetime <= now:
        return "0 00:00:00"

    delta = target_datetime - now
    total_seconds = int(delta.total_seconds())

    days = total_seconds // 86400
    remaining_seconds = total_seconds % 86400

    hours = remaining_seconds // 3600
    remaining_seconds %= 3600

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    return f"{days} {hours:02d}:{minutes:02d}:{seconds:02d}"


async def add_pinned_message(channel_id: int, message_id: int):
    """Добавляет информацию о закрепленном сообщении"""
    async with Session() as session:
        pinned_msg = PinnedMessage(
            channel_id=channel_id,
            message_id=message_id
        )
        session.add(pinned_msg)
        await session.commit()


async def get_pinned_messages(channel_id: int) -> List[PinnedMessage]:
    """Возвращает список закрепленных сообщений для канала"""
    async with Session() as session:
        stmt = select(PinnedMessage).where(
            PinnedMessage.channel_id == channel_id
        ).order_by(PinnedMessage.pinned_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()


async def unpin_oldest_message(channel_id: int):
    """Открепляет самое старое сообщение если их больше 3"""
    pinned_messages = await get_pinned_messages(channel_id)

    if len(pinned_messages) > 3:
        oldest_message = pinned_messages[0]
        try:
            await bot.unpin_chat_message(chat_id=channel_id, message_id=oldest_message.message_id)
        except Exception as e:
            print(f"Error unpinning message: {e}")

        async with Session() as session:
            await session.delete(oldest_message)
            await session.commit()


async def pin_message(user_id, message_id):
    await bot.pin_chat_message(user_id, message_id)

    # Сохраняем информацию о закреплении
    await add_pinned_message(user_id, message_id)

    # Проверяем и открепляем старое сообщение если нужно
    await unpin_oldest_message(user_id)
