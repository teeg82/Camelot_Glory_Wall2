#! /bin/sh

source slack.sh

docker run -it --rm --name camelot_glory_wall -e SLACK_TOKEN=$SLACK_TOKEN -e SLACK_USERNAME=$SLACK_USERNAME paulrichter/camelot_glory_wall:1.0 sh
#| pbcopy
