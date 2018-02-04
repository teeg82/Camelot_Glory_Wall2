#! /bin/sh

cd ./app
docker build -t paulrichter/camelot_glory_wall:1.0 .

cd ../db
docker build -t paulrichter/camelot_db:1.0 .

cd ..
