
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

    # Обработка команды "!Админы"
    if message.reply_to_message and message.text and (message.text.strip() == "!Админы" or message.text.strip() == "!админы"):
        await bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=MASSAGE_ADMIN,
            reply_to_message_id=message.reply_to_message.message_id 
        )
        return

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
        

    # if 0.012 > rnd_sut: 
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
            # Передаём user_id для использования памяти сообщений
            
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

                # --- NEW: split long messages and escape markdown ---
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