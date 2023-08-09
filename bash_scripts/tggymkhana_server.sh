#!/bin/bash

echo "$1 the docker container" 
docker $1 tgbot-gymkhana-ggp_python_1
docker $1 tgbot-gymkhana-ggp_mongodb_1
