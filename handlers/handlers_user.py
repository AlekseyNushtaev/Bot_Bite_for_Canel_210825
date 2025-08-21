import asyncio
import datetime

import aiohttp

from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from moviepy import VideoFileClip

from bot import bot
from config import LOCALIZATION_LANG, REWARD_PER_VIEW, SPONSOR_CHANNEL_LINK, MAX_VIDEOS_PER_CYCLE, COOLDOWN_DAYS, \
    NUMBER_GIFT_7_8, NUMBER_GIFT_17_18, BONUS_AFTER_17, MIN_WITHDRAWAL, POSTBACK_START, TIMEZONE
from db.data import video_dct
from db.utils import user_exists, add_user, update_messages_to_del, delete_messages, get_user_by_id, update_user, \
    update_user_blocked, update_user_unblocked, add_user_without_start
from keyboard import create_kb
from lexicon import lexicon_dct

router: Router = Router()


# @router.message(F.from_user.id == 1012882762)
# async def process_load_video(mes: types.Message):
#     try:
#         print(mes.photo[0].file_id)
#     except:
#         pass
#     try:
#         print(mes.video_note.file_id)
#     except:
#         pass


class WithdrawalStates(StatesGroup):
    WAITING_DETAILS = State()   # Ожидание реквизитов
    WAITING_AMOUNT = State()    # Ожидание суммы


@router.message(Command("start"))
async def start_command(message: types.Message, command: CommandObject):
    user_in_db = await user_exists(message.from_user.id)
    if user_in_db:
        await delete_messages(message.from_user.id)
        sent_message = await message.answer(text=lexicon_dct[LOCALIZATION_LANG]['text_main_menu'],
                             reply_markup=create_kb(
                                 1,
                                 look_video=lexicon_dct[LOCALIZATION_LANG]['button_main_video'],
                                 profil=lexicon_dct[LOCALIZATION_LANG]['button_main_profile'],
                                 vivod=lexicon_dct[LOCALIZATION_LANG]['button_main_money_back']
                             ))
        await update_messages_to_del(message.from_user.id, str(sent_message.message_id))

    else:
        start_arg = command.args
        if start_arg:
            arg = command.args
        else:
            arg = '000'

        postback_link = POSTBACK_START.replace('{{sub_id}}', arg.replace('_', '.'))
        async with aiohttp.ClientSession() as session:
            async with session.get(postback_link) as response:
                print(response.status)

        await add_user(message.from_user.id,
                       message.from_user.username,
                       message.from_user.first_name,
                       message.from_user.last_name,
                       arg)

        if message.from_user.first_name:
            caption = (lexicon_dct[LOCALIZATION_LANG]['welcome_title_with_first_name'] + message.from_user.first_name +
                       '!\n' + lexicon_dct[LOCALIZATION_LANG]['welcome_body'])
        else:
            caption = (lexicon_dct[LOCALIZATION_LANG]['welcome_title_without_first_name'] + '\n' +
                       lexicon_dct[LOCALIZATION_LANG]['welcome_body'])
        sent_message = await message.answer_video(
            video=video_dct['gif_start'],
            caption=caption,
            reply_markup=create_kb(1, look_video_first=lexicon_dct[LOCALIZATION_LANG]['welcome_button'])
        )
        await update_messages_to_del(message.from_user.id, str(sent_message.message_id))


@router.callback_query(F.data.startswith("look_video"))
async def look_video(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    await delete_messages(callback.from_user.id)
    user_dct = await get_user_by_id(callback.from_user.id)
    if callback.data == 'look_video_first':
        text = '⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️0%...\n' + lexicon_dct[LOCALIZATION_LANG]['preload_text']
        first_message = await callback.message.answer(text)
        await asyncio.sleep(0.5)
        text = '⬛️⬛️⬛️⬜️⬜️⬜️⬜️⬜️⬜️⬜️30%...\n' + lexicon_dct[LOCALIZATION_LANG]['preload_text']
        await bot.edit_message_text(text=text,
                                    chat_id=callback.from_user.id,
                                    message_id=first_message.message_id)
        await asyncio.sleep(0.5)
        text = '⬛️⬛️⬛️⬛️⬛️⬛️⬜️⬜️⬜️⬜️60%...\n' + lexicon_dct[LOCALIZATION_LANG]['preload_text']
        await bot.edit_message_text(text=text,
                                    chat_id=callback.from_user.id,
                                    message_id=first_message.message_id)
        await asyncio.sleep(0.5)
        text = '⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬜️90%...\n' + lexicon_dct[LOCALIZATION_LANG]['preload_text']
        await bot.edit_message_text(text=text,
                                    chat_id=callback.from_user.id,
                                    message_id=first_message.message_id)
        await asyncio.sleep(0.5)
        text = '⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️100%...\n' + lexicon_dct[LOCALIZATION_LANG]['full_load_text']
        await bot.edit_message_text(text=text,
                                    chat_id=callback.from_user.id,
                                    message_id=first_message.message_id)
        await asyncio.sleep(1)
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=first_message.message_id)

    if callback.data not in ['look_video', 'look_video_first']:
        user_dct['like_counter'] += 1
        user_dct['video_counter'] += 1
        user_dct['balance'] += REWARD_PER_VIEW

    if user_dct['video_counter'] == 26:
        user_dct['video_counter'] = 1

    if user_dct['like_counter'] > 10 and not user_dct['in_chanel']:
        if not user_dct['time_stop']:
            user_dct['time_stop'] = datetime.datetime.now(TIMEZONE) + datetime.timedelta(days=COOLDOWN_DAYS)
        time_stop = user_dct['time_stop']
        if time_stop.tzinfo is None:
            time_stop = time_stop.replace(tzinfo=TIMEZONE)
        if datetime.datetime.now(TIMEZONE) > user_dct['time_stop']:
            sent_message = await callback.message.answer(
                text=lexicon_dct[LOCALIZATION_LANG]['no_video_text'],
                reply_markup=create_kb(1, back_to_main=lexicon_dct[LOCALIZATION_LANG]['main_menu_button']))
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[

                    [InlineKeyboardButton(
                        text=lexicon_dct[LOCALIZATION_LANG]['main_menu_button'],
                        callback_data="back_to_main"
                    )],
                    [InlineKeyboardButton(
                        text=lexicon_dct[LOCALIZATION_LANG]['to_chanel_button'],
                        url=SPONSOR_CHANNEL_LINK.replace('{{sub_id}}', user_dct['sub_id'])
                    )]
            ])
            sent_message = await callback.message.answer(
                text=lexicon_dct[LOCALIZATION_LANG]['text_to_10_messsage'](user_dct['time_stop']),
                reply_markup=keyboard
            )
        user_dct["messages_to_del"] = sent_message.message_id

    elif user_dct['like_counter'] > MAX_VIDEOS_PER_CYCLE:
        if not user_dct['time_stop']:
            user_dct['time_stop'] = datetime.datetime.now(TIMEZONE) + datetime.timedelta(days=COOLDOWN_DAYS)
        time_stop = user_dct['time_stop']
        if time_stop.tzinfo is None:
            time_stop = time_stop.replace(tzinfo=TIMEZONE)
        if datetime.datetime.now(TIMEZONE) > time_stop:
            sent_message = await callback.message.answer(
                text=lexicon_dct[LOCALIZATION_LANG]['no_video_text'],
                reply_markup=create_kb(1, back_to_main=lexicon_dct[LOCALIZATION_LANG]['main_menu_button']))
        else:
            sent_message = await callback.message.answer(
                text=lexicon_dct[LOCALIZATION_LANG]['text_end_cycle'](user_dct['time_stop']),
                reply_markup=create_kb(1, back_to_main=lexicon_dct[LOCALIZATION_LANG]['main_menu_button']))
        user_dct["messages_to_del"] = sent_message.message_id

    else:
        text = lexicon_dct[LOCALIZATION_LANG]['video_text_1'](user_dct['balance'])
        sent_message_1 = await callback.message.answer(text=text)

        if user_dct['in_chanel']:
            text = lexicon_dct[LOCALIZATION_LANG]['video_text_2_in'](user_dct['like_counter'], user_dct['balance'])
        else:
            text = lexicon_dct[LOCALIZATION_LANG]['video_text_2_out'](user_dct['like_counter'], user_dct['balance'])
        sent_message_2 = await callback.message.answer(text=text)

        if user_dct['like_counter'] == NUMBER_GIFT_7_8 and not user_dct['is_gift']:
            user_dct['is_gift'] = True
            sent_message_3 = await callback.message.answer(
                text=lexicon_dct[LOCALIZATION_LANG]['text_between_7_and_8'],
                reply_markup=create_kb(1,
                                       to_chanel=lexicon_dct[LOCALIZATION_LANG]['button_between_7_and_8_yes'],
                                       look_video=lexicon_dct[LOCALIZATION_LANG]['button_between_7_and_8_no'])
                  )
        elif user_dct['like_counter'] == NUMBER_GIFT_17_18 and not user_dct['is_gift_2']:
            user_dct['is_gift_2'] = True
            text = lexicon_dct[LOCALIZATION_LANG]['text_between_17_and_18'](user_dct['balance'])
            user_dct['balance'] += BONUS_AFTER_17
            sent_message_3 = await callback.message.answer(
                text=text,
                reply_markup=create_kb(1, look_video=lexicon_dct[LOCALIZATION_LANG]['button_main_video']))

        else:

            sent_message_3 = await callback.message.answer_video(
                video=video_dct[user_dct["video_counter"]],
                reply_markup=create_kb(1,
                                       not_answer_1=lexicon_dct[LOCALIZATION_LANG]['button_like'],
                                       not_answer_2=lexicon_dct[LOCALIZATION_LANG]['button_unlike'],
                                       cancel_look=lexicon_dct[LOCALIZATION_LANG]['button_cancel_look'])
            )
            with VideoFileClip(f'videos/{user_dct["video_counter"]}.mp4') as video:
                seconds = int(2 * video.duration) // 3
                await asyncio.sleep(seconds)
            await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                                message_id=sent_message_3.message_id,
                                                reply_markup=create_kb(1,
                                                                       look_video_1=lexicon_dct[LOCALIZATION_LANG]['button_like'],
                                                                       look_video_2=lexicon_dct[LOCALIZATION_LANG]['button_unlike'],
                                                                       cancel_look=lexicon_dct[LOCALIZATION_LANG]['button_cancel_look'])
                                                )

        messages_to_del = ', '.join([str(sent_message_1.message_id),
                                     str(sent_message_2.message_id),
                                     str(sent_message_3.message_id)])
        user_dct["messages_to_del"] = messages_to_del
    await update_user(user_dct)


@router.callback_query(F.data.startswith('not_answer'))
async def not_answer(callback: types.CallbackQuery):
    await callback.answer(lexicon_dct[LOCALIZATION_LANG]['awarning_to_look'], show_alert=True)


@router.callback_query(F.data == 'cancel_look')
async def cancel_look(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    await delete_messages(callback.from_user.id)
    sent_message = await callback.message.answer(
        text=lexicon_dct[LOCALIZATION_LANG]['text_cancel_look'],
        reply_markup=create_kb(1,
                               look_video=lexicon_dct[LOCALIZATION_LANG]['button_return_to_look'],
                               back_to_main=lexicon_dct[LOCALIZATION_LANG]['button_cancel_look_yes'])
    )
    await update_messages_to_del(callback.from_user.id, str(sent_message.message_id))


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    sent_message = await callback.message.edit_text(
        text=lexicon_dct[LOCALIZATION_LANG]['text_main_menu'],
        reply_markup=create_kb(
             1,
             look_video=lexicon_dct[LOCALIZATION_LANG]['button_main_video'],
             profil=lexicon_dct[LOCALIZATION_LANG]['button_main_profile'],
             vivod=lexicon_dct[LOCALIZATION_LANG]['button_main_money_back']
                                     ))
    await update_messages_to_del(callback.from_user.id, str(sent_message.message_id))


@router.callback_query(F.data == 'to_chanel')
async def to_chanel(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    user_dct = await get_user_by_id(callback.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(
            text=lexicon_dct[LOCALIZATION_LANG]['to_chanel_button'],
            url=SPONSOR_CHANNEL_LINK.replace('{{sub_id}}', user_dct['sub_id'].replace('_', '.'))
        )],
        [InlineKeyboardButton(
            text=lexicon_dct[LOCALIZATION_LANG]['button_check_bonus'],
            callback_data="check_bonus"
        )]
    ])
    await callback.message.edit_text(text=lexicon_dct[LOCALIZATION_LANG]['text_bonus_between_7_and_8'],
                                     reply_markup=keyboard)


@router.callback_query(F.data == 'check_bonus')
async def check_bonus(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    user_dct = await get_user_by_id(callback.from_user.id)
    if not user_dct['in_chanel']:
        await callback.answer(text=lexicon_dct[LOCALIZATION_LANG]['awarning_not_in_chanel'])
    else:
        pass


@router.callback_query(F.data == 'take_gift_78')
async def check_bonus(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    # user_id = callback.from_user.id
    # user_dct = await get_user_by_id(user_id)
    # user_dct['balance'] += BONUS_BETWEEN_7_AND_8
    await callback.message.edit_text(text=lexicon_dct[LOCALIZATION_LANG]['gift_after_7_text'],
                                     reply_markup=create_kb(1, look_video=lexicon_dct[LOCALIZATION_LANG]['back_button']))
    # await update_user(user_dct)


@router.callback_query(F.data == 'profil')
async def profile(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    user_id = callback.from_user.id
    user_dct = await get_user_by_id(user_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(
            text=lexicon_dct[LOCALIZATION_LANG]['button_main_video'],
            callback_data="look_video"
        )],

        [InlineKeyboardButton(
            text=lexicon_dct[LOCALIZATION_LANG]['bonus_chanel_button'],
            url=SPONSOR_CHANNEL_LINK.replace('{{sub_id}}', user_dct['sub_id'].replace('_', '.'))
        )],
        [InlineKeyboardButton(
            text=lexicon_dct[LOCALIZATION_LANG]['back_button'],
            callback_data="back_to_main"
        )]
    ])
    simbol = '❗️'
    if user_dct['status'] == 'in_chanel':
        simbol = '✅'
    chanel_status = lexicon_dct[LOCALIZATION_LANG][user_dct['status']]
    text = lexicon_dct[LOCALIZATION_LANG]['profile_text'](user_dct, simbol, chanel_status)
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)


@router.callback_query(F.data == 'vivod')
async def profile(callback: types.CallbackQuery):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    user_id = callback.from_user.id
    user_dct = await get_user_by_id(user_id)
    if user_dct['balance'] < MIN_WITHDRAWAL:
        text = lexicon_dct[LOCALIZATION_LANG]['alert_min_withdrawal']
        await callback.answer(text, show_alert=True)
        return
    await delete_messages(callback.from_user.id)
    sent_message = await callback.message.answer_video(
        video=video_dct['vivod'],
        reply_markup=create_kb(2,
                               phone=lexicon_dct[LOCALIZATION_LANG]['phone_button'],
                               paypal=lexicon_dct[LOCALIZATION_LANG]['paypal_button'],
                               binance=lexicon_dct[LOCALIZATION_LANG]['binance_button'],
                               card=lexicon_dct[LOCALIZATION_LANG]['card_button'],
                               back_to_main=lexicon_dct[LOCALIZATION_LANG]['back_button']))
    await update_messages_to_del(callback.from_user.id, str(sent_message.message_id))


@router.callback_query(F.data.in_(['phone', 'paypal', 'binance', 'card']))
async def set_withdrawal_method(callback: types.CallbackQuery, state: FSMContext):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    await delete_messages(callback.from_user.id)
    await state.set_state(WithdrawalStates.WAITING_DETAILS)
    await state.update_data(method=callback.data)

    sent_message = await callback.message.answer(
        text=lexicon_dct[LOCALIZATION_LANG]['text_requisites'],
        reply_markup=create_kb(1, back_to_main_vivod=lexicon_dct[LOCALIZATION_LANG]['back_button'])
    )
    await update_messages_to_del(callback.from_user.id, str(sent_message.message_id))


@router.message(WithdrawalStates.WAITING_DETAILS)
async def process_details(message: types.Message, state: FSMContext):
    await message.delete()
    await state.update_data(details=message.text)
    await state.set_state(WithdrawalStates.WAITING_AMOUNT)

    sent_message = await message.answer(
        text=lexicon_dct[LOCALIZATION_LANG]['text_withdrawal_value'],
        reply_markup=create_kb(1, back_to_main_vivod=lexicon_dct[LOCALIZATION_LANG]['back_button'])
    )
    user_id = message.from_user.id
    user_dct = await get_user_by_id(user_id)
    lst = user_dct['messages_to_del'].split(', ')
    lst.append(str(sent_message.message_id))
    user_dct['messages_to_del'] = ', '.join(lst)
    await update_user(user_dct)


@router.message(WithdrawalStates.WAITING_AMOUNT)
async def process_amount(message: types.Message, state: FSMContext):
    await add_user_without_start(message.from_user.id,
                                 message.from_user.username,
                                 message.from_user.first_name,
                                 message.from_user.last_name)
    await message.delete()
    user_id = message.from_user.id
    user_dct = await get_user_by_id(user_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(
            text=lexicon_dct[LOCALIZATION_LANG]['bonus_chanel_button'],
            url=SPONSOR_CHANNEL_LINK.replace('{{sub_id}}', user_dct['sub_id'].replace('_', '.'))
        )],
        [InlineKeyboardButton(
            text=lexicon_dct[LOCALIZATION_LANG]['back_button'],
            callback_data="back_to_main_vivod"
        )]
    ])
    lst = user_dct['messages_to_del'].split(', ')

    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        sent_message_1 = await message.answer(
            text=lexicon_dct[LOCALIZATION_LANG]['text_no_digits'])
        sent_message_2 = await message.answer(
            text=lexicon_dct[LOCALIZATION_LANG]['text_withdrawal_value'],
            reply_markup=create_kb(1, back_to_main_vivod=lexicon_dct[LOCALIZATION_LANG]['back_button'])
        )
        lst.append(str(sent_message_1.message_id))
        lst.append(str(sent_message_2.message_id))
        user_dct['messages_to_del'] = ', '.join(lst)
        await update_user(user_dct)
        return

    if amount > user_dct['balance']:
        text = lexicon_dct[LOCALIZATION_LANG]['back_button'](user_dct['balance'], amount)
        sent_message = await message.answer(
            text=text,
            reply_markup=keyboard
        )
        lst.append(str(sent_message.message_id))
        user_dct['messages_to_del'] = ', '.join(lst)
        await update_user(user_dct)
        return

    # Обновляем баланс
    user_dct['balance'] -= amount
    await update_user(user_dct)
    text = lexicon_dct[LOCALIZATION_LANG]['text_withdrawal_good'](amount)
    sent_message = await message.answer(
        text=text,
        reply_markup=keyboard)
    lst.append(str(sent_message.message_id))
    user_dct['messages_to_del'] = ', '.join(lst)
    await update_user(user_dct)
    await state.clear()


@router.callback_query(F.data == 'back_to_main_vivod')
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await add_user_without_start(callback.from_user.id,
                                 callback.from_user.username,
                                 callback.from_user.first_name,
                                 callback.from_user.last_name)
    await state.clear()
    await delete_messages(callback.from_user.id)
    sent_message = await callback.message.answer(
        text=lexicon_dct[LOCALIZATION_LANG]['text_main_menu'],
        reply_markup=create_kb(
             1,
             look_video=lexicon_dct[LOCALIZATION_LANG]['button_main_video'],
             profil=lexicon_dct[LOCALIZATION_LANG]['button_main_profile'],
             vivod=lexicon_dct[LOCALIZATION_LANG]['button_main_money_back']
                                     ))
    await update_messages_to_del(callback.from_user.id, str(sent_message.message_id))


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    await add_user_without_start(event.from_user.id,
                                 event.from_user.username,
                                 event.from_user.first_name,
                                 event.from_user.last_name)
    await update_user_blocked(event.from_user.id)
    print('block')


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    await add_user_without_start(event.from_user.id,
                                 event.from_user.username,
                                 event.from_user.first_name,
                                 event.from_user.last_name)
    await update_user_unblocked(event.from_user.id)
    print('unblock')






