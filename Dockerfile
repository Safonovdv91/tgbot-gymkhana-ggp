FROM python:3.9.16-slim-buster
COPY . .
WORKDIR .
RUN python3 -m pip install -r requirements.txt
 # пробрасывание во внешний мир порт
CMD python aio_bot_start.py