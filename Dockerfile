# Использование базового образа Python
FROM python:3.11.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y ffmpeg python3-venv && apt-get clean

# Обновление pipdoc
RUN pip install --upgrade pip
RUN pip install pip-audit

# Установка зависимостей Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Установка рабочей директории
WORKDIR /app

# Копирование всех файлов из текущей директории
COPY . /app

# Команда запуска приложения
CMD ["python", "app/bot.py"]
