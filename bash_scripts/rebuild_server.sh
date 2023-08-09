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

echo "Удаляем образ"

docker rmi tgbot-gymkhana-ggp_python

echo "Образ удален, запускаем новый"

docker-compose up -d

echo "Server up!"

