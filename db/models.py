from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# Настройка асинхронного подключения к SQLite3
DB_URL = "sqlite+aiosqlite:///db/database.db"
engine = create_async_engine(DB_URL)  # Асинхронный движок SQLAlchemy
Session = async_sessionmaker(expire_on_commit=False, bind=engine)  # Фабрика сессий


class Base(DeclarativeBase, AsyncAttrs):
    """Базовый класс для декларативных моделей с поддержкой асинхронных атрибутов"""
    pass


class User(Base):
    """Модель для хранения запросов на подписку"""
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)  # ID пользователя Telegram
    sub_id = Column(String, nullable=True)  # Уникальный id трекера
    username = Column(String, nullable=True)  # @username пользователя
    first_name = Column(String, nullable=True)  # Имя пользователя
    last_name = Column(String, nullable=True)  # Фамилия пользователя
    messages_to_del = Column(String, nullable=True)  # Сообщения для удаления
    in_chanel = Column(Boolean, default=False)  # Статус в канале
    time_chanel_in = Column(DateTime, nullable=True)  # Время вступления в канал
    time_chanel_out = Column(DateTime, nullable=True)  # Время выхода из канала
    is_gift = Column(Boolean, default=False)  # Предложен ли подарок
    is_gift_2 = Column(Boolean, default=False)  # Предложен ли подарок
    time_start = Column(DateTime, nullable=True)  # Время входа
    time_stop = Column(DateTime, nullable=True)  # Время начала таймера
    balance = Column(Integer, default=0)  # Денежный баланс
    status = Column(String, default='not_in_chanel')  # Статус в канале
    like_counter = Column(Integer, default=1)  # Счетчик лайков
    video_counter = Column(Integer, default=1)  # Счетчик видео
    user_is_block = Column(Boolean, default=False)  # Флаг блокировки пользователя
    time_block = Column(DateTime, nullable=True)  # Время блокировки бота
    time_unblock = Column(DateTime, nullable=True)  # Время разблокировки бота


class PinnedMessage(Base):
    """Модель для хранения закрепленных сообщений в канале"""
    __tablename__ = "pinned_messages"

    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger)  # ID канала
    message_id = Column(Integer)  # ID сообщения
    pinned_at = Column(DateTime, nullable=True)  # Время закрепления


async def create_tables():
    """Создает таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
