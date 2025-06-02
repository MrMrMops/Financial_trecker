FROM python:3.11

WORKDIR /usr/src/app/backend

COPY requirements.txt ./                 
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN chmod +x /usr/src/app/backend/docker/entrypoint.sh

CMD ["sh", "/entrypoint.sh"]