# Butler Eugene Telegram Bot

## Описание

Butler Eugene — Это слабый, сделпнный наспех проект использующий искуственный интеллект для поддержания общения и актива телеграмм чата.

## Быстрый старт

### 1. Создайте файл `.env`

Скопируйте `.env.example` в `.env` и заполните своими данными:

```sh
cp .env.example .env
```

**Заполните значения в .env:**
- `TOKEN`=токен
- `TARGET_CHAT_ID`=чат
- `OLLAMA_HOST`=http://localhost:11434
- `DEAR`=idжениха
- `DEAR_A`=@ссылкажениха
- `HI_CHANNEL`=каналПриветствия
- `DEAR_NAME`=ник

Создайте пустой файл `app/output.txt`

### 2. Запуск и остановка бота

Запустите проект:
```sh
docker compose up -d --build;
```

Остановите проект:
```sh
docker compose down;
```

Боты будут работать в фоне, автоматически модерируя чат.

## Структура проекта
```
│   .env - основной .env файл
│   .env.example
│   .gitignore
│   docker-compose.yml
│   Dockerfile
│   readme.md
│   requirements.txt - библиотеки
│
└───app
    │   .gitattributes
    │   BLACKLIST.txt - чёрный список
    │   bot.py - основные handler работы бота
    │   config.py - база данных и промпт для работы бота
    │   main.log
    │   main.py - файл подгружающий bot.py
    │   marry.txt - статус отношений
    │   mat_list.txt - список запрещённых слов
    │   Modelfile - старый промпт нейросети (ollama create eug -f ./Modelfile)
    │   mood.txt - настроение смайликами
    │   output.txt - друзья
    │   p.py - рисование досье человека и досье бота
    │   p.txt - вариации запретного слова
    │   readme.md - старое описание, до контейнеризации
    │   result.jpg - последнее сформировавшееся досье
    │   utils.py - основные фукнции работы бота
    │
    ├───ava
    │       default_avatar.jpg
    │
    ├───clean - файлы дебага
    │       old_bot.py
    │
    ├───photo
    │       Arial.ttf
    │       background.jpg
    │       background_info.jpg
    │       DSEraserCyr.ttf
    │       EmojiOne.ttf
    │       Goose.ttf
    │       NotoSans-Regular.ttf
    │
    └───__pycache__
```

## Безопасность
- Все чувствительные данные хранятся только в `.env` (не добавляйте его в репозиторий)
- Для публикации используйте `.env.example` как шаблон

## Лицензия
MIT

