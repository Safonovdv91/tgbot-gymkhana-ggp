#!/bin/bash

prefix=tgbot-gymkhana-ggp_python
suffix=`eval date +%s`  # Ключ "+%s" характерен для GNU-версии 'date'.
imagename=$prefix.$suffix
echo "Save old image, with new name $imagename"
docker tag tgbot-gymkhana-ggp_python $imagename
echo "Отображаем что есть в докере..."

docker ps
docker stop tgbot-gymkhana-ggp_mongodb_1
docker stop tgbot-gymkhana-ggp_python_1

echo "Контейнеры остановлены"

docker rm tgbot-gymkhana-ggp_mongodb_1
docker rm tgbot-gymkhana-ggp_python_1

echo "Особенность моего проекта, поденяем необходимый конфиг и путь до бд"
cp ../../config_bot.py ../aio_bot/config_bot.py
cp ../../docker-compose.yml ../docker-compose.yml
echo "Кода-нибудь я престану быть тупым и заведу это все в .env"

echo "Удаляем образ"

docker rmi tgbot-gymkhana-ggp_python

echo "Образ удален, запускаем новый"

docker-compose up -d

echo "Server up!"

