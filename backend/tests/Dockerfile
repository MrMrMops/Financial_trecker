FROM python:3.11

# Папка, в которой будут запускаться тесты
WORKDIR /usr/src/app/tests

# Скопировать requirements.txt из родительской папки
COPY ../requirements.txt /usr/src/app/requirements.txt

# Установить зависимости
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# Копируем backend/app и backend/tests
COPY ../app /usr/src/app/app
COPY . /usr/src/app/tests

# Устанавливаем PYTHONPATH на корень backend
ENV PYTHONPATH=/usr/src/app

CMD ["pytest", "-v"]
