import datetime
from pprint import pprint

import aiohttp

from aiogram import Router

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated

from bot import bot
from config import SPONSOR_CHANNEL_ID, LOCALIZATION_LANG, NUMBER_GIFT_7_8, SPONSOR_CHANNEL_LINK, POSTBACK_SUBSCRIBE, \
    TIMEZONE, BONUS_BETWEEN_7_AND_8
from db.utils import get_user_by_id, delete_messages, update_user
from keyboard import create_kb
from lexicon import lexicon_dct

router: Router = Router()


@router.chat_member()
async def handle_chat_member_update(update: ChatMemberUpdated):
    if update.chat.id != SPONSOR_CHANNEL_ID:
        return
    user_id = update.new_chat_member.user.id
    user_dct = await get_user_by_id(user_id)
    if update.old_chat_member.status == "left" and update.new_chat_member.status == "member":

        async with aiohttp.ClientSession() as session:
            async with session.get(POSTBACK_SUBSCRIBE.replace('{{sub_id}}', user_dct['sub_id'].replace('_', '.'))) as response:
                print(response.status)
        await delete_messages(user_id)
        user_dct['in_chanel'] = True
        user_dct['status'] = 'in_chanel'
        user_dct['time_chanel_in'] = datetime.datetime.now(TIMEZONE)
        if user_dct['like_counter'] == NUMBER_GIFT_7_8:
            user_dct['balance'] += BONUS_BETWEEN_7_AND_8
            sent_message = await bot.send_message(chat_id=user_id,
                                                  text=lexicon_dct[LOCALIZATION_LANG]['text_chanel_in'],
                                                  reply_markup=create_kb(1,
                                                                         take_gift_78=lexicon_dct[LOCALIZATION_LANG][
                                                                             'button_between_7_and_8_yes'],
                                                                         look_video=lexicon_dct[LOCALIZATION_LANG][
                                                                             'button_main_video']))
        else:
            sent_message = await bot.send_message(chat_id=user_id,
                                                  text=lexicon_dct[LOCALIZATION_LANG]['text_chanel_in'],
                                                  reply_markup=create_kb(1, look_video=lexicon_dct[LOCALIZATION_LANG][
                                                      'button_main_video']))
        user_dct['messages_to_del'] = sent_message.message_id
    elif update.old_chat_member.status != "left" and update.new_chat_member.status == "left":
        user_dct['in_chanel'] = False
        user_dct['status'] = 'leave_chanel'
        user_dct['time_chanel_out'] = datetime.datetime.now(TIMEZONE)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[

            [InlineKeyboardButton(
                text=lexicon_dct[LOCALIZATION_LANG]['to_chanel_button'],
                url=SPONSOR_CHANNEL_LINK.replace('{{sub_id}}', user_dct['sub_id'])
            )],
            [InlineKeyboardButton(
                text=lexicon_dct[LOCALIZATION_LANG]['button_main_video'],
                callback_data="look_video"
            )]
        ])
        sent_message = await bot.send_message(chat_id=user_id,
                                              text=lexicon_dct[LOCALIZATION_LANG]['text_chanel_out'],
                                              reply_markup=keyboard)
        lst = user_dct['messages_to_del'].split(', ')
        lst.append(str(sent_message.message_id))
        user_dct['messages_to_del'] = ', '.join(lst)
    await update_user(user_dct)




