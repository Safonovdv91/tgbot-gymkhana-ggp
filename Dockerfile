FROM python:3.10-bullseye
COPY . .
WORKDIR .
RUN python3 -m pip install -r requirements.txt
 # пробрасывание во внешний мир порт
CMD python app.py