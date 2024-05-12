# Використовуємо офіційний образ Python
FROM python:3.9-slim

# Встановлюємо poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Створюємо та встановлюємо домашню роботу "Персональний помічник"
WORKDIR /app
COPY . .


# Вказуємо команду для запуску застосунку
CMD [ "python", "personal_assistant.py"]

