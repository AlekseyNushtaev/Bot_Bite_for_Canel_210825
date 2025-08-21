import pytz
from dotenv import load_dotenv
import os
from typing import Set, Optional

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота Telegram
TG_TOKEN: Optional[str] = os.environ.get("TG_TOKEN")

# Множество ID администраторов бота
ADMIN_IDS: Set[int] = {int(x) for x in os.environ.get("ADMIN_IDS", "").split()} if os.environ.get("ADMIN_IDS") else set()
SPONSOR_CHANNEL_LINK: Optional[str] = os.environ.get("SPONSOR_CHANNEL_LINK")
SPONSOR_CHANNEL_ID: Optional[int] = int(os.environ.get("SPONSOR_CHANNEL_ID"))
REWARD_PER_VIEW: Optional[float] = float(os.environ.get("REWARD_PER_VIEW"))
BONUS_BETWEEN_7_AND_8: Optional[int] = int(os.environ.get("BONUS_BETWEEN_7_AND_8"))
NUMBER_GIFT_7_8: Optional[int] = int(os.environ.get("NUMBER_GIFT_7_8"))
NUMBER_GIFT_17_18: Optional[int] = int(os.environ.get("NUMBER_GIFT_17_18"))
BONUS_AFTER_17: Optional[int] = int(os.environ.get("BONUS_AFTER_17"))
MAX_VIDEOS_PER_CYCLE: Optional[int] = int(os.environ.get("MAX_VIDEOS_PER_CYCLE"))
COOLDOWN_DAYS: Optional[int] = int(os.environ.get("COOLDOWN_DAYS"))
MIN_WITHDRAWAL: Optional[int] = int(os.environ.get("MIN_WITHDRAWAL"))
LOCALIZATION_LANG: Optional[str] = os.environ.get("LOCALIZATION_LANG")
POSTBACK_START: Optional[str] = os.environ.get("POSTBACK_START")
POSTBACK_SUBSCRIBE: Optional[str] = os.environ.get("POSTBACK_SUBSCRIBE")
AUTO_PUSH_RUNNING = [False]  # Используем список для mutable значения
AUTO_PUSH_DAY = [1]
TIMEZONE_STR: Optional[str] = os.environ.get("TIMEZONE_STR")
TIMEZONE = pytz.timezone(TIMEZONE_STR)
