#! /bin/sh

source slack.sh

docker-compose -p camelot $@
