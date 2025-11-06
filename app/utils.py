import os
import re
import requests
import json
import subprocess
from config import ALLOWED_LINK_HOSTS, PROBABILITY_DIVIDER, MAT_PING_FILE, POR_PING_FILE, OLLAMA_HOST, BLACKLIST_FILE, CHARACTER_DESCRIPTION
from p import get_time_and_date_info
import aiohttp
import os
from collections import defaultdict, deque

# Глобальная память сообщений: user_id -> deque([msg1, msg2, ...])
user_message_memory = defaultdict(lambda: deque(maxlen=5))

def add_message_to_memory(user_id, user_msg, assistant_msg):
    user_message_memory[user_id].append({"role": "user", "content": user_msg})
    user_message_memory[user_id].append({"role": "assistant", "content": assistant_msg})


def get_memory_for_user(user_id):
    return list(user_message_memory[user_id])

async def download_avatar_and_generate_output(bot, user_id, display_name, count, fr_state):
    photos = await bot.get_user_profile_photos(user_id, limit=1, offset=0)
    avatar_path = f"app/ava/photo_{user_id}.jpg"
    default_avatar_path = "app/photo/default_avatar.jpg"

    # if os.path.exists(avatar_path):
    #     os.remove(avatar_path)

    avatar_saved = False
    if photos.total_count > 0:
        max_size = 0
        max_photo = None
        for photo in photos.photos[0]:
            if photo.width * photo.height > max_size:
                max_size = photo.width * photo.height
                max_photo = photo

        try:
            photo = await bot.get_file(max_photo.file_id)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.telegram.org/file/bot{bot.token}/{photo.file_path}") as response:
                    with open(avatar_path, "wb") as f:
                        f.write(await response.content.read())
            avatar_saved = True
        except Exception as e:
            avatar_saved = False

    if not avatar_saved or not os.path.exists(avatar_path):
        avatar_path = default_avatar_path

    output_string = f"{user_id} {display_name} {avatar_path} {fr_state} {count}"
    return output_string, avatar_path


def update_entry(identifier, new_status=None, new_value=None):
    file_path = "app/output.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []
    result = None

    for line in lines:
        parts = line.strip().split()

        if parts[0] == str(identifier):
            if new_value is None:
                current_value = int(parts[-1])
                new_value = current_value - 1

                if new_value < 0:
                    new_value = 0 
                    return False 
            else:
                new_value = int(new_value)

            parts[-1] = str(new_value)

            if new_status is not None:
                parts[-2] = new_status

            result = ' '.join(parts)

        updated_lines.append(' '.join(parts))

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(updated_lines) + '\n')

    return result

def get_all_ids():
    file_path = 'app/output.txt'
    ids = []
    friend_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()
        ids.append(parts[0])
        
        if parts[-2] in ['ДРУГ', 'ПОДРУГА']:
            friend_count += 1

    return ids, friend_count

def get_count_by_id(identifier):
    file_path = "app/output.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()

        if parts[0] == str(identifier):
            try:
                return int(parts[-1])
            except ValueError:
                return 0

    return 0  

def change_last_digit(new_digit):
    file_name = 'app/output.txt'
    with open(file_name, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        parts = line.strip().split()
        parts[-1] = str(new_digit)
        updated_lines.append(' '.join(parts) + '\n')

    with open(file_name, 'w') as file:
        file.writelines(updated_lines)

def check_id_in_file(identifier):
    file_path = "app/output.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()

        if parts[0] == str(identifier):
            return True

    return False

def load_file_lines(filename):
    try:
        with open(filename, "r") as file:
            content = file.read().strip().lower()
            return content.split(',')
    except FileNotFoundError:
        return []

def find_links(text):
    url_pattern = re.compile(r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")
    return url_pattern.findall(text)

def is_link_allowed(link):
    for allowed_host in ALLOWED_LINK_HOSTS:
        if allowed_host in link.lower():
            return True
    return False

async def is_chat_admin(user_id: int, chat_id: int, bot) -> bool:
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


def update_model_with_ollama_modefile():
    try:
        modelfile_path = os.path.expanduser('~/Modelfile')
        
        process = subprocess.Popen(['ollama', 'create', 'eug', '-f', modelfile_path], 
                                   stdin=subprocess.PIPE, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 0:
            return True
        else:
            print(f"Ошибка создания модели: {error.decode('utf-8')}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды: {e}")
        return False
    

def get_moods():
    with open('app/mood.txt', 'r') as file:
        moods = file.read().splitlines()
    mood_1 = moods[0]
    mood_2 = moods[1]
    return mood_1, mood_2

def update_model_with_ollama_modefile_friend():
    try:
        modelfile_path = os.path.expanduser('~/Modelfile_fr')
        process = subprocess.Popen(['ollama', 'create', 'eug', '-f', modelfile_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode == 0:
            return True
        else:
            print(f"Ошибка создания модели: {error.decode('utf-8')}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды: {e}")
        return False
    
def check_friend_or_girlfriend(user_id):
    file_name = 'app/output.txt'
    with open(file_name, 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()
        if parts[0] == str(user_id):
            if parts[3] == "ДРУГ":
                return True
            elif parts[3] == "ПОДРУГА":
                return False

    return None  

def text_friend_or_girlfriend(user_id):
    file_name = 'app/output.txt'
    with open(file_name, 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()
        if parts[0] == str(user_id):
            if parts[3] == "ДРУГ":
                return "ДРУГ"
            elif parts[3] == "ПОДРУГА":
                return "ПОДРУГА"

    return "НЕЗНАКОМЕЦ"

def update_model_with_ollama_modefile_ut():
    try:
        modelfile_path = os.path.expanduser('~/Modelfile_ut')
        process = subprocess.Popen(['ollama', 'create', 'eug', '-f', modelfile_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode == 0:
            return True
        else:
            print(f"Ошибка создания модели: {error.decode('utf-8')}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды: {e}")
        return False

async def calculate_reply_probability(message_text: str, user_id: int, chat_id: int, bot) -> float:
    message_length = len(message_text)
    base_probability = 0

    if message_length <= 5:
        base_probability = 0
    else:
        base_probability = message_length / 100 / PROBABILITY_DIVIDER
        # if await is_chat_admin(user_id, chat_id, bot):
        #     update_model_with_ollama_modefile_friend()
        #     base_probability += 0.08
        # else:
        #     update_model_with_ollama_modefile()

    return min(base_probability, 0.70)

def get_current_state_description():
    time_info = get_time_and_date_info()
    hour = time_info["hour"]
    minute = time_info["minute"]
    day = time_info["day"]
    month_ru = time_info["month_ru"]
    day_of_week_ru = time_info["day_of_week_ru"]
    time_of_day = time_info["time_of_day"]

    description = f"Сейчас {time_of_day}, {day_of_week_ru}, {day} {month_ru} в {hour}:{minute}. (используй дату только если нужно)"
    return description

def run_gemma_with_description(mess, user_id=None):
    get_time_and_date_info()
    # mood_1, mood_2 = get_moods()
    now_moment = get_current_state_description()

    # Читаем информацию о супругах
    marriage_info = ""
    try:
        with open('app/marry.txt', 'r') as file:
            marriage_info = file.read().strip()
        if marriage_info:
            marriage_info = f"\nИнформация о супругах:\n{marriage_info}"
    except FileNotFoundError:
        marriage_info = ""

    history = []
    if user_id is not None:
        memory = get_memory_for_user(user_id)
        history.extend(memory)

    payload = {
        "model": "gemma3:12b",
        "messages": [
            {
                "role": "system",
                "content": f"""{CHARACTER_DESCRIPTION}

{now_moment}{marriage_info}"""
            },
            *history,
            {
                "role": "user",
                "content": mess
            }
        ],
        "stream": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    url = "http://localhost:11434/v1/chat/completions"

    try:
        response = requests.post(f"{OLLAMA_HOST}/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        choices = data.get("choices", [])
        if choices:
            text = choices[0]["message"]["content"].strip()
            # убираем точку
            if text.endswith("."):
                text = text[:-1]
            return text
        else:
            return "Ответ не получен от модели"
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к локальному Ollama: {e}")
        return None


def find_profanity(message_text):
    mat_words = load_file_lines(MAT_PING_FILE)
    message_text_lower = message_text.lower()
    words_in_message = re.findall(r'\b\w+\b', message_text_lower)
    if any(mat_word in words_in_message for mat_word in mat_words):
        return True
    return False

def clean_and_remove_duplicates(word):
    cleaned_word = re.sub(r'[^a-zA-Zа-яА-Я0-9@]', '', word)    
    result = []
    prev_char = ''
    for char in cleaned_word:
        if char != prev_char:
            result.append(char)
        prev_char = char
    
    return ''.join(result)

def escape_markdown(text):
    parts = re.split(r'(```[\s\S]*?```)', text)
    result = []

    for part in parts:
        if part.startswith('```') and part.endswith('```'):
            result.append(part)
        else:
            escaped = re.sub(r'([*_])', r'\\\1', part)
            result.append(escaped)

    return ''.join(result)



def find_porn(message_text):
    mat_words = load_file_lines(POR_PING_FILE)
    message_text_lower = message_text.lower()
    words_in_message = re.findall(r'\b\w+\b', message_text_lower)
    words_in_message = [clean_and_remove_duplicates(word) for word in words_in_message]
    if any(mat_word in words_in_message for mat_word in mat_words):
        print(words_in_message)
        return True
    return False

def is_user_blacklisted(user_id: int) -> bool:
    try:
        with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
            return str(user_id) in {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return False

def add_user_to_blacklist(user_id: int) -> bool:
    if is_user_blacklisted(user_id):
        return False
    with open(BLACKLIST_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user_id}\n")
    return True

def get_blacklist_count() -> int:
    try:
        with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except FileNotFoundError:
        return 0