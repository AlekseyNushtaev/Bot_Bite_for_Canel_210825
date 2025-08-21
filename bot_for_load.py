import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import TG_TOKEN

# Списки ключей из оригинального файла
VIDEO_DCT_KEYS = [
    'gif_start', 'vivod', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23, 24, 25
]

POST_DICT_IN_KEYS = [
    '1', '2', '3', '4', '5', '6', '7', '8', '8_1', '8_2', '8_3', '8_4', '8_5',
    '8_6', '9', '10', '11', '12'
]

POST_DICT_OUT_KEYS = [
    '1', '1_2', '2', '2_1', '3', '3_1', '4', '5', '5_1', '6', '7', '7_1',
    '7_2', '7_3', '7_4', '8', '8_1', '8_2', '8_3', '8_4', '8_5', '8_6', '9',
    '10', '11', '12'
]

ALL = VIDEO_DCT_KEYS + POST_DICT_IN_KEYS + POST_DICT_OUT_KEYS

class MediaCollection(StatesGroup):
    waiting_for_media = State()
    processing = State()

async def start_collection(message: types.Message, state: FSMContext):
    await state.set_state(MediaCollection.waiting_for_media)
    await state.update_data(
        media_list=[],
        current_index=0
    )
    await message.answer("Отправьте 71 медиафайл для формирования файла данных")

async def handle_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_list = data['media_list']
    current_index = data['current_index']

    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.animation:
        file_id = message.animation.file_id
    elif message.video_note:
        file_id = message.video_note.file_id

    if file_id:
        media_list.append(file_id)
        current_index += 1
        if current_index < 71:
            await message.answer(f'Ожидается файл {ALL[current_index]}')
        await state.update_data(
            media_list=media_list,
            current_index=current_index
        )

        if current_index == 71:
            await state.set_state(MediaCollection.processing)
            await process_media(message, state)
        else:
            await message.answer(f"Получено {current_index}/71 файлов")

def format_dict(dct, keys):
    """Форматирует словарь в стиле data.py"""
    lines = []
    for key in keys:
        if isinstance(key, str):
            lines.append(f"    '{key}': '{dct[key]}',")
        else:
            lines.append(f"    {key}: '{dct[key]}',")
    return '{\n' + '\n'.join(lines) + '\n}'

async def process_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_list = data['media_list']

    # Формируем словари
    video_dct = {}
    for i, key in enumerate(VIDEO_DCT_KEYS):
        video_dct[key] = media_list[i]

    post_dict_in = {}
    for i, key in enumerate(POST_DICT_IN_KEYS):
        post_dict_in[key] = media_list[27 + i]

    post_dict_out = {}
    for i, key in enumerate(POST_DICT_OUT_KEYS):
        post_dict_out[key] = media_list[45 + i]

    # Форматируем словари
    video_dct_str = format_dict(video_dct, VIDEO_DCT_KEYS)
    post_dict_in_str = format_dict(post_dict_in, POST_DICT_IN_KEYS)
    post_dict_out_str = format_dict(post_dict_out, POST_DICT_OUT_KEYS)

    # Формируем содержимое файла
    file_content = f"""video_dct = {video_dct_str}

post_dict_in = {post_dict_in_str}

post_dict_out = {post_dict_out_str}
"""

    # Сохраняем файл
    with open('db/new_data.py', 'w', encoding='utf-8') as f:
        f.write(file_content)

    await message.answer("Файл db/new_data.py успешно создан!")
    await state.clear()

async def main():
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_collection, Command("start"))
    dp.message.register(handle_media, MediaCollection.waiting_for_media)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
