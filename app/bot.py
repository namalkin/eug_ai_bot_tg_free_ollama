# В прошлом развёлся с виконтессой де Флер
import time
import asyncio
import logging
import sys
import random
import os
import aiohttp
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReactionTypeEmoji, InputFile, FSInputFile, ChatPermissions
from aiogram.methods import DeleteWebhook, SendChatAction
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

from p import passport_img_draw, info_img_draw
from config import TOKEN, TARGET_CHAT_ID, MSK, EMOJI_REACTIONS, HI_CHANNEL, MESSAGE_WELCOM, MASSAGE_MAT, MASSAGE_LINK, welcome_timestamp, ADMINS, AVATAR_FOLDER, INFO_FILE, PROBABILITY_DIVIDER, DEAR, DEAR_A, DEAR_NAME, MASSAGE_ADMIN, SLOT_EMOJIS
from utils import find_links, is_link_allowed, calculate_reply_probability, run_gemma_with_description, find_profanity, update_model_with_ollama_modefile_ut, update_entry, get_count_by_id, get_all_ids, download_avatar_and_generate_output, check_id_in_file, change_last_digit, check_friend_or_girlfriend, get_moods, text_friend_or_girlfriend, find_porn
from utils import add_message_to_memory, escape_markdown
from utils import is_user_blacklisted, add_user_to_blacklist, get_blacklist_count

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
logger = logging.getLogger(__name__)
dp = Dispatcher()

def is_admin(user_id):
    return user_id in ADMINS

@dp.message(Command("start_poll"))
async def start_poll_handler(message: Message) -> None:
    if message.chat.type != "private":
        return
    if not is_admin(message.from_user.id):
        await message.reply("Ты не можешь так поступить.")
        return
    question = "LL. Давайте соберёмся и решим уйдёт ли Проджект из чата?"
    options = ["ДаДадА 1000%", "СЖЕЧ! УВОЛИТЬ!", "НЕТ! 5 ЖЁН И 5 МУЖЕЙ В ОДНОЙ СЕМЬЕ! ВСЕ СЕМЬЯ", "не позволю!", "Прощаем", "Прощай", "Я ещё не решил"]
    
    await bot.send_poll(chat_id=TARGET_CHAT_ID, question=question, options=options, is_anonymous=False)

@dp.message(Command("msg_namalkin_in"))
async def msg_namalkin_in_handler(message: Message, bot: Bot) -> None:
    if message.chat.type != "private":
        return
    if not is_admin(message.from_user.id):
        await message.reply("Ты не можешь так поступить.")
        return
    text = ""
    for line in message.text.splitlines()[1:]:
        text += line + "\n"
    await bot.send_message(TARGET_CHAT_ID, text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("mood"))
async def mood_handler(message: Message, bot: Bot) -> None:
    if message.chat.type != "private":
        return
    if not is_admin(message.from_user.id):
        await message.reply("Ты не можешь так поступить.")
        return
    moods = message.text.splitlines()[1:]
    if len(moods) != 2:
        await message.reply("Нужно указать два настроения.")
        return
    mood_1, mood_2 = moods
    with open('app/mood.txt', 'w') as file:
        file.write(mood_1 + "\n" + mood_2)
    await message.reply("Настроение записано.")

@dp.message(Command("sboross"))
async def msg_namalkin_in_handler(message: Message, bot: Bot) -> None:
    if message.chat.type != "private":
        return
    if not is_admin(message.from_user.id):
        await message.reply("Ты не можешь так поступить.")
        return
    change_last_digit(5)

    await message.reply("Обновлено на 5")

@dp.message(Command("msg_namalkin_llin"))
async def msg_namalkin_in_handler(message: Message, bot: Bot) -> None:
    if message.chat.type != "private":
        return
    
    if not is_admin(message.from_user.id):
        await message.reply("Ты не можешь так поступить.")
        return
    
    lines = message.text.splitlines()
    
    if len(lines) > 1:
        reply_to_message_id = lines[1].strip()
        if reply_to_message_id.isdigit():
            reply_to_message_id = int(reply_to_message_id)
        else:
            reply_to_message_id = None
    else:
        reply_to_message_id = None

    text = "\n".join(lines[2:]) 
    text = run_gemma_with_description(text)

    if reply_to_message_id is not None:
        await bot.send_message(
            TARGET_CHAT_ID,
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=reply_to_message_id
        )
    else:
        await bot.send_message(
            TARGET_CHAT_ID,
            text,
            parse_mode=ParseMode.MARKDOWN
        )


@dp.message(Command("msg_namalkin_hasband"))
async def msg_namalkin_in_handler(message: Message, bot: Bot) -> None:
    if message.chat.type != "private":
        return
    
    if not is_admin(message.from_user.id):
        await message.reply("Ты не можешь так поступить.")
        return
    
    lines = message.text.splitlines()
    
    if len(lines) > 1:
        reply_to_message_id = lines[1].strip()
        if reply_to_message_id.isdigit():
            reply_to_message_id = int(reply_to_message_id)
        else:
            reply_to_message_id = None
    else:
        reply_to_message_id = None

    text = "\n".join(lines[2:]) 
    text = run_gemma_with_description(text)
    text = f"{DEAR_A} \n {text}"
    pol_m = types.InlineKeyboardButton(text='Согласна!', callback_data=f'new_ok__{DEAR}')
    pol_b = types.InlineKeyboardButton(text='НЕТ', callback_data=f'new_n__{DEAR}')
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[pol_m, pol_b]])
    text = escape_markdown(text)
    await bot.send_message(
        TARGET_CHAT_ID,
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )

@dp.message(CommandStart())
async def msg_info_in_handler(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    
    if message.chat.type != "private":
        return
    
    if is_user_blacklisted(message.from_user.id):
        return
    # print(f"Ввёл info в лс [{message.from_user.full_name}](tg://user?id={message.from_user.id})")
    logger.info(f"Ввёл info в лс [{message.from_user.full_name}](tg://user?id={message.from_user.id})")
    try:
        with open("app/output.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    display_name = message.from_user.username if message.from_user.username else "hero"

    output_string, avatar_path = await download_avatar_and_generate_output(bot, user_id, display_name, get_count_by_id(user_id), text_friend_or_girlfriend(user_id))
    
    for line in lines:
        if str(user_id) in line:
            pass
    
    result_image_path = info_img_draw(display_name, user_id, avatar_path, text_friend_or_girlfriend(user_id), get_count_by_id(user_id))
    photo_path = FSInputFile(result_image_path)
    await message.reply_photo(
        photo=photo_path,
        caption="Ваши права 🫖",
        parse_mode="HTML",
        disable_notification=True 
    )


@dp.message(Command("st"))
async def msg_info_in_handler(message: Message, bot: Bot) -> None:
    if message.chat.type != "private":
        return
    
    if not is_admin(message.from_user.id):
        await message.reply("Ты не можешь так поступить.")
        return
    id_list, friend_count = get_all_ids()
    mood_1, mood_2 = get_moods()
    result_image_path = passport_img_draw(mood_1, mood_2, friend_count, get_blacklist_count(), PROBABILITY_DIVIDER)
    photo_path = FSInputFile(result_image_path)
    friend_count = types.InlineKeyboardButton(text='Добавить в друзья', callback_data='new_frnd')
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[friend_count]])
    caption = "\n".join(message.text.splitlines()[1:])
    await bot.send_photo(
        chat_id=TARGET_CHAT_ID,
        photo=photo_path,
        caption=caption,
        parse_mode="Markdown",
        disable_notification=True,
        reply_markup=markup
    )
    

@dp.message()
async def echo_handler(message: Message, bot: Bot) -> None:
    if message.chat.id != TARGET_CHAT_ID:
        return
    
    # if message.text and message.text.strip().lower() == "!спин":
    #     spin_result = [random.choice(SLOT_EMOJIS) for _ in range(3)]
    #     result_text = " ".join(spin_result)
        
    #     comment = ""
    #     if len(set(spin_result)) == 1:  # Все три одинаковые
    #         comment = run_gemma_with_description(f"Пользватель сыграл в казино  {result_text}. Произошло невероятное! все три символа совпали! опиши это событие с восторгом. Но очень кратко.")
    #     elif len(set(spin_result)) == 2:  # Две одинаковые
    #         comment = run_gemma_with_description(f"Пользватель сыграл в казино {result_text}. Два символа совпали! это хороший знак! прокомментируй это. Но очень кратко.")
    #     else:  # Все разные
    #         comment = run_gemma_with_description(f"Пользватель сыграл в казино {result_text}. Все символы разные. Скажи что-нибудь утешительное. Но очень кратко.")

    #     await message.reply(
    #         f"Вам выпало: {result_text} \n\n{comment}",
    #         parse_mode=ParseMode.MARKDOWN
    #     )
    #     return

    if message.text and message.text.strip().lower() == "!досье":
        user_id = message.from_user.id
        
        if is_user_blacklisted(user_id):
            return

        display_name = message.from_user.username if message.from_user.username else "hero"
        output_string, avatar_path = await download_avatar_and_generate_output(
            bot, 
            user_id, 
            display_name, 
            get_count_by_id(user_id), 
            text_friend_or_girlfriend(user_id)
        )
        
        result_image_path = info_img_draw(
            display_name, 
            user_id, 
            avatar_path, 
            text_friend_or_girlfriend(user_id), 
            get_count_by_id(user_id)
        )
        photo_path = FSInputFile(result_image_path)
        await message.reply_photo(
            photo=photo_path,
            caption="Ваши права 🫖",
            parse_mode="HTML",
            disable_notification=True 
        )
        return

    # "!Админы"
    # if message.reply_to_message and message.text and (message.text.strip() == "!Админы" or message.text.strip() == "!админы"):
    #     await bot.send_message(
    #         chat_id=TARGET_CHAT_ID,
    #         text=MASSAGE_ADMIN,
    #         reply_to_message_id=message.reply_to_message.message_id
    #     )
    #     return

    global welcome_timestamp
    if welcome_timestamp and time.time() - welcome_timestamp < 20 * 60:
        logger.info("20 минут не прошли")
        return
    
    if message.forward_from_chat and message.forward_from_chat.id == HI_CHANNEL:
        if message.media_group_id:
            if not hasattr(bot, 'last_media_group') or bot.last_media_group != message.media_group_id:
                await message.reply(MESSAGE_WELCOM)
                bot.last_media_group = message.media_group_id
        else:
            await message.reply(MESSAGE_WELCOM)
            welcome_timestamp = time.time()
            logger.info("Сделан ответ на пост")
        return


    if (
        message.reply_to_message
        and message.text
        and message.text.strip().lower() == "дворецкий чс"
        and is_admin(message.from_user.id)
        and message.chat.id == TARGET_CHAT_ID
    ):
        target_id = message.reply_to_message.from_user.id
        if is_user_blacklisted(target_id):
            await message.reply("Пользователь уже в чёрном списке.")
            return  
        else:
            add_user_to_blacklist(target_id)
            await message.reply(f"Пользователь {target_id} добавлен в чёрный список.")
            return  

    rnd_sut = random.random()
        

    # if 0.072 > rnd_sut: 
    #     await send_special_message(bot, "напиши интересную историю или интересный факт, забавно и без упоминания стран.")

    if is_user_blacklisted(message.from_user.id):
        return

    id_list, friend_count = get_all_ids()
    if not str(message.from_user.id) in id_list:
        return

    if message.sticker:
        chance = 0.06
    elif message.text:
        chance = 0
        if find_profanity(message.text):
            delete_button = types.InlineKeyboardButton(text='Я ошибся (удалить)', callback_data='delete_message')
            markup = types.InlineKeyboardMarkup(inline_keyboard=[[delete_button]])
            await message.reply(MASSAGE_MAT, reply_markup=markup)
            return
        for link in find_links(message.text):
            if not is_link_allowed(link):
                delete_button = types.InlineKeyboardButton(text='Я ошибся (удалить)', callback_data='delete_message')
                markup = types.InlineKeyboardMarkup(inline_keyboard=[[delete_button]])
                await message.reply(MASSAGE_LINK, reply_markup=markup)
                return
        
        chance = await calculate_reply_probability(message.text, message.from_user.id, message.chat.id, bot)
        # if 'дворецк' in message.text.lower() and update_entry(identifier=message.from_user.id):
        if 'дворецк' in message.text.lower():
            chance = 1
    else:
        chance = 0
    
    logger.info(f"ШАНС: {round(chance, 3):.3f}/{round(rnd_sut, 3):.3f} - {message.from_user.id:<10} {message.from_user.full_name}")

    if rnd_sut < chance:
        try:
            mess = ""
            if 'дворецк' in message.text.lower():
                mess += "Кажется, к тебе обратились в чате."
            
            if 656071688 == message.from_user.id: mess += "\n\n И это твой любимый уважаемый Дедушка. и он"
            else:
                if check_friend_or_girlfriend(message.from_user.id): mess += f"Твоего друга зовут *{message.from_user.full_name}* и он "
                else: mess += f"Твою подругу зовут *{message.from_user.full_name}* и она "

            if message.reply_to_message:
                if message.reply_to_message.from_user.id == bot.id:
                    if message.sticker:
                        mess += f"ответил{'а' if not check_friend_or_girlfriend(message.from_user.id) else ''} боту эмодзи стикером: {message.sticker.emoji}"
                    else:
                        mess += f"ответил{'а' if not check_friend_or_girlfriend(message.from_user.id) else ''} боту: {message.text}"
                else:
                    if message.sticker:
                        mess += f"ответил{'а' if not check_friend_or_girlfriend(message.from_user.id) else ''} кому-то эмодзи стикером: {message.sticker.emoji}"
                    else:
                        mess += f"ответил{'а' if not check_friend_or_girlfriend(message.from_user.id) else ''} кому-то: {message.text}"
            else:
                if message.sticker:
                    mess += f"отправил{'а' if not check_friend_or_girlfriend(message.from_user.id) else ''} эмодзи стикер: {message.sticker.emoji}"
                else:
                    mess += f"написал{'а' if not check_friend_or_girlfriend(message.from_user.id) else ''}: {message.text}"

            # if 'ворецк' in message.from_user.full_name: mess += "\n\nТак же он твой Коллега, тоже дворецкий и хороший друг, он как и вы служит этому чату"
            if 5130935865  == message.from_user.id: mess += "\n\nТак же он твой Коллега, тоже дворецкий и служит этому чату сейчас"
            if 5353068028 == message.from_user.id: mess += "\n\nЕё называй Ванилька "
            if 7251027656 == message.from_user.id: mess += "\n\nЕго называй Михаил "
            if 1273867987 == message.from_user.id: mess += "\n\n Это Namalkin и он тот кто пригласил тебя в этот чат"
            # if os.path.getsize('app/marry.txt') != 0: 
            #     if DEAR == message.from_user.id: mess += f"\n\nВам написала ваша супруа {DEAR_NAME} "

            mess += "\n\nТы учавствуешь в беседе поэтому отвечай без приветствий, пиши ответ сразу без вступления."

            if message.sticker:
                logger.info(f"{message.from_user.full_name} - {message.sticker.emoji}")
            else:
                logger.info(f"{message.from_user.full_name} - {message.text}")
            
            await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
            
            response = run_gemma_with_description(mess, user_id=message.from_user.id)
            if response:
                add_message_to_memory(message.from_user.id, message.text, response)
                response_text = response
                emoji = next((char for char in response_text if char in EMOJI_REACTIONS), None)
                if emoji:
                    try: await message.react([ReactionTypeEmoji(emoji=emoji)])
                    except Exception as e: print(f"Error {e} {emoji}")
                index = response_text.find("Евгений:")
                if index != -1:
                    new_mess = response_text[index + 2:]
                else:
                    new_mess = response_text

                MAX_LEN = 4096
                parts = []
                text = new_mess
                while len(text) > MAX_LEN:
                    parts.append(text[:MAX_LEN])
                    text = text[MAX_LEN:]
                if text:
                    parts.append(text)

                first = True
                for part in parts:
                    safe_part = part  
                    try:
                        if first:
                            await message.reply(safe_part, parse_mode=ParseMode.MARKDOWN)
                            first = False
                        else:
                            await message.answer(safe_part, parse_mode=ParseMode.MARKDOWN)
                    except Exception as e:
                        try:
                            if first:
                                await message.reply(safe_part)
                                first = False
                            else:
                                await message.answer(safe_part)
                        except Exception as e2:
                            logging.error(f"Error occurred: {e2}")
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            pass

user_ids = set()
vb_ids = set()
@dp.callback_query()
async def callback_query_handler(callback: types.CallbackQuery, bot: Bot):
    if callback.data == 'delete_message':
        if callback.from_user.id in ADMINS:
            await callback.message.delete()
            await callback.answer()
        else:
            await callback.answer("Сэр, вы не можете со мной так поступить!", show_alert=True)
    if callback.data == 'new_frnd':
        if is_user_blacklisted(callback.from_user.id):
            await callback.answer("Вы не можете быть ему другом, обращайтесь к Namalkin", show_alert=True)
            return
        elif check_id_in_file(callback.from_user.id):
            await callback.answer("Мы с вами уже в дружеских отношениях", show_alert=True)
            return    
        elif callback.from_user.id in user_ids:
            await callback.answer("Не стоит держать меня за дурака! Мы же уже начали знакомство...", show_alert=True)
            return
        else:
            await callback.answer("Превосходно! Будем дружить!", show_alert=True)
            pol_m = types.InlineKeyboardButton(text='ДРУГ', callback_data=f'new_m__{callback.from_user.id}')
            pol_b = types.InlineKeyboardButton(text='ПОДРУГА', callback_data=f'new_b__{callback.from_user.id}')
            markup = types.InlineKeyboardMarkup(inline_keyboard=[[pol_m, pol_b]])
            await bot.send_message(
                chat_id=TARGET_CHAT_ID, 
                text=f"Отлично, [{callback.from_user.full_name}](tg://user?id={callback.from_user.id}), давайте поладим! Будем знакомы",
                parse_mode="Markdown",
                reply_markup=markup
            )
            user_ids.add(callback.from_user.id)            

    data = callback.data.split('__')
    if data[0] == 'new_m':
        if callback.from_user.id != int(data[1]):
            await callback.answer("Вы не можете нажать на эту кнопку!", show_alert=True)
            return
        user_id = callback.from_user.id
        try:
            with open("app/output.txt", "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        if callback.from_user.id in vb_ids:
            await callback.answer("Вы уже выбрали")
            return
        vb_ids.add(callback.from_user.id)

        output_string, avatar_path = await download_avatar_and_generate_output(bot, callback.from_user.id, callback.from_user.username, 5, "ДРУГ")

        updated_lines = []
        for line in lines:
            if str(user_id) in line:
                updated_lines.append(output_string + "\n")
            else:
                updated_lines.append(line)
        
        if not any(str(user_id) in line for line in lines):
            updated_lines.append(output_string + "\n")
        
        with open("app/output.txt", "w") as f:
            f.writelines(updated_lines)

        result_image_path = info_img_draw(callback.from_user.username, callback.from_user.id, avatar_path, "ДРУГ", 5)
        photo_path = FSInputFile(result_image_path)
        try:
            await callback.message.delete() 
            await bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=photo_path,
                caption=f"Ваше досье сэр [{callback.from_user.full_name}](tg://user?id={callback.from_user.id}) 🫖 \n\nЯ рад объявить, что у меня появился новый друг и сэр.",
                parse_mode="Markdown",
                disable_notification=True 
            )
            await callback.answer()
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            
    if data[0] == 'new_b':
        if callback.from_user.id != int(data[1]):
            await callback.answer("Вы не можете нажать на эту кнопку!", show_alert=True)
            return
        user_id = callback.from_user.id
        try:
            with open("app/output.txt", "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        output_string, avatar_path = await download_avatar_and_generate_output(bot, callback.from_user.id, callback.from_user.username, 5, "ПОДРУГА")
        updated_lines = []
        for line in lines:
            if str(user_id) in line:
                updated_lines.append(output_string + "\n")
            else:
                updated_lines.append(line)
        
        if not any(str(user_id) in line for line in lines):
            updated_lines.append(output_string + "\n")
        
        with open("app/output.txt", "w") as f:
            f.writelines(updated_lines)
        result_image_path = info_img_draw(callback.from_user.username, callback.from_user.id, avatar_path, "ПОДРУГА", 5)
        photo_path = FSInputFile(result_image_path)
        try:
            await bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=photo_path,
                caption=f"Ваши права уважаемая [{callback.from_user.full_name}](tg://user?id={callback.from_user.id}) 🫖 \n\n Весьма рад знакомству",
                parse_mode="Markdown",
                disable_notification=True 
            )
            await callback.message.delete() 
            await callback.answer()
        except Exception as e:
            logging.error(f"Error occurred: {e}")
    if data[0] == 'new_ok':
        if callback.from_user.id != int(data[1]):
            await callback.answer("Вы не можете нажать на эту кнопку!", show_alert=True)
            return
        user_id = callback.from_user.id
        text = f"Вашим дорогим супругом является {DEAR_NAME}"
        with open('app/marry.txt', 'a') as file: 
            file.write(text + '\n')
        
        text = run_gemma_with_description(f"Твой возлюбленный {DEAR_NAME} дал своё согласие на твоё предложение руки и сердца! ура")
        text = escape_markdown(f"{DEAR_A} \n {text}")
        
        await bot.send_message(
            TARGET_CHAT_ID,
            text,
            parse_mode=ParseMode.MARKDOWN,
        )
        
    if data[0] == 'new_n':
        if callback.from_user.id != int(data[1]):
            await callback.answer("Вы не можете нажать на эту кнопку!", show_alert=True)
            return
        user_id = callback.from_user.id
        text = run_gemma_with_description(f"Твоя возлюбленная {DEAR_NAME} отказала на твоё предложение руки и сердца! :< ")
        text = escape_markdown(f"{DEAR_A} \n {text}")
        
        await bot.send_message(
            TARGET_CHAT_ID,
            text,
            parse_mode=ParseMode.MARKDOWN,
        )
        

async def send_special_message(bot: Bot, mess):
    await bot.send_chat_action(chat_id=TARGET_CHAT_ID, action=ChatAction.TYPING)
    await bot.send_message(chat_id=TARGET_CHAT_ID, text=run_gemma_with_description(mess), parse_mode=ParseMode.MARKDOWN)
    # print(f"Сообщение отправлено в {datetime.now(MSK).strftime('%H:%M %d-%m-%Y')} по МСК.")
    logger.info(f"Сообщение отправлено в {datetime.now(MSK).strftime('%H:%M %d-%m-%Y')} по МСК.")

async def send_special_message_update(bot: Bot, mess):
    change_last_digit(12)
    print("время вышло")
    await bot.send_chat_action(chat_id=TARGET_CHAT_ID, action=ChatAction.TYPING)
    id_list, friend_count = get_all_ids()
    mood_1, mood_2 = get_moods()
    result_image_path = passport_img_draw(mood_1, mood_2, friend_count, get_blacklist_count(), PROBABILITY_DIVIDER)
    photo_path = FSInputFile(result_image_path)
    friend_count = types.InlineKeyboardButton(text='Добавить в друзья', callback_data='new_frnd')
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[friend_count]])
    await bot.send_photo(
        chat_id=TARGET_CHAT_ID,
        photo=photo_path,
        caption=run_gemma_with_description(mess),
        parse_mode=ParseMode.MARKDOWN,
        disable_notification=True,
        reply_markup=markup
    )
    # print(f"Сообщение отправлено в {datetime.now(MSK).strftime('%H:%M %d-%m-%Y')} по МСК.")
    logger.info(f"Сообщение отправлено в {datetime.now(MSK).strftime('%H:%M %d-%m-%Y')} по МСК.")



async def setup_scheduler(bot: Bot) -> None:
    scheduler = AsyncIOScheduler(timezone=MSK)

    # scheduler.add_job(send_special_message, CronTrigger(hour=7, minute=0), args=[bot, "Напиши про себя русский стих, с рифмами как в русских стихах, напиши стих о себе и о твоём предстоящем дне"])
    # scheduler.add_job(send_special_message, CronTrigger(hour=15, minute=0), args=[bot, "Напиши про себя русский стих, с рифмами как в русских стихах, напиши стих о себе и о доме"])
    # scheduler.add_job(send_special_message, CronTrigger(hour=17, minute=0), args=[bot, "Напиши про себя русский стих, с рифмами как в русских стихах, напиши стих о себе и о своём вечере"])
    # scheduler.add_job(send_special_message, CronTrigger(hour=21, minute=2), args=[bot, "Напиши про себя русский стих, с рифмами как в русских стихах, напиши стих о себе и о том что ночь близка"])

    # scheduler.add_job(send_special_message_update, CronTrigger(hour=0, minute=46), args=[bot, "Напиши что запросы для друзей обновлены и ты снова готов отвечать им"])
    # scheduler.add_job(send_special_message_update, CronTrigger(hour=12, minute=0), args=[bot, "Напиши что запросы для друзей обновлены и ты снова готов отвечать им"])
    scheduler.add_job(send_special_message_update, CronTrigger(hour=21, minute=0), args=[bot, "Напиши торжественную речь!"])

    scheduler.start()

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot(DeleteWebhook(drop_pending_updates=True))

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('app/main.log')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info('Программа запущена')
    await setup_scheduler(bot)

    await dp.start_polling(bot)